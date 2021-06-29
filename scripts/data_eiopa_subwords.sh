#!/bin/bash
# full pipeline EIOPA that you can run to prepare the data and train the model
# Use this script from the root!

COPY=YES # set this variable to YES, if the generated files should be directly copied to the model_input folder
USE_SUBWORDS=YES # use of subword splitting
USE_KNOWN_AND_UNKNOWN_NAMES=YES
BILINGUAL=NO # need 2 version of test templates
EXAMPLES_PER_TEMPLATE=130
VOCAB_SIZE=15000


if [ $USE_KNOWN_AND_UNKNOWN_NAMES = YES ]; then
  export EXAMPLES_PER_TEMPLATE=$(($EXAMPLES_PER_TEMPLATE / 2))
fi

echo "Making directories..."
mkdir -p ./data/eiopa/2_interim/logs
mkdir -p ./data/eiopa/3_processed/logs
mkdir -p ./data/eiopa/4_vocabularies

DATA_DIR=data/eiopa/1_external # input data location
OUT_DIR=data/eiopa/3_processed
INT_DIR=data/eiopa/2_interim
DICT_DIR=data/eiopa/4_vocabularies
TEST_TEMPLATES=test_templates
COUNT_TEST=$((`ls -l $DATA_DIR/$TEST_TEMPLATES/*.csv | wc -l` ))
if [ $BILINGUAL = "YES" ]; then
  COUNT_TEST=$((2*COUNT_TEST))
  TEST_TEMPLATES=$TEST_TEMPLATES,"$TEST_TEMPLATES"_dutch
fi

echo "Generate job ID"
ID_SHORT=$RANDOM
ID=$(date +"%d-%m_%H-%M")_"$ID_SHORT"
echo "Job ID is set at:"
echo "$ID"

echo 'Generating data (train, validation)...'
python src/generator.py \
  --templates $DATA_DIR/templates.csv \
  --output $INT_DIR --id "$ID" --type train_val_nl \
  --graph-data-path $DATA_DIR --input-language en\
  --examples-per-template $EXAMPLES_PER_TEMPLATE

if [ $BILINGUAL = "YES" ]; then
  echo 'Generating dutch data (train, validation)...'
  # since we use append mode in the generator for writing files, we
  # can directly append the dutch templates on the train_val set
  python src/generator.py \
    --templates $DATA_DIR/templates_dutch.csv \
    --output $INT_DIR --id "$ID" --type train_val_nl \
    --graph-data-path $DATA_DIR --input-language nl \
    --examples-per-template $EXAMPLES_PER_TEMPLATE
fi

if [ $USE_KNOWN_AND_UNKNOWN_NAMES = "YES" ]; then
  echo 'Generating data (train, validation) for DE insurers...'
  python src/generator.py \
    --templates $DATA_DIR/templates_DE.csv \
    --output $INT_DIR --id "$ID" --type train_val_de \
    --graph-data-path $DATA_DIR --input-language en \
    --examples-per-template $EXAMPLES_PER_TEMPLATE

  if [ $BILINGUAL = "YES" ]; then
  echo 'Generating dutch data (train, validation) for DE insurers...'
  python src/generator.py \
    --templates $DATA_DIR/templates_dutch_DE.csv \
    --output $INT_DIR --id "$ID" --type train_val_de \
    --graph-data-path $DATA_DIR --input-language nl \
    --examples-per-template $EXAMPLES_PER_TEMPLATE
  fi

  echo "Concatenate files with NL and DE insurance names..."
  for L in nl ql; do
    cat $INT_DIR/data_"$ID"-train_val_nl.$L $INT_DIR/data_"$ID"-train_val_de.$L > $INT_DIR/data_"$ID"-train_val.$L
  done

  echo "Create dictionaries"
  # shellcheck disable=SC2002
  cat $INT_DIR/data_"$ID"-train_val_nl.nl  |
    tr -s '[:space:]' '\n' | # turns every space into a \n, so every word into new line; several spaces into single one
    sort |
    uniq -c > $INT_DIR/dict.pg.interim # counts how many duplicate lines there are, returns count before line

    cat $INT_DIR/dict.pg.interim | # $DATA_DIR/dict.iwslt.reversed.en |
    sort -k2 |
    uniq -f 1 | # filter out double elements
    sort -k1,1 -b -n -r -k2 | # sort based on first column, numeric values reversed
    head -n "$((VOCAB_SIZE - 4))" | # display first n elements of file
    awk '{ print $2 " " $1 }' > $DICT_DIR/dict-"$ID".nl

  python subword-nmt/subword_nmt/get_vocab.py \
    --input $INT_DIR/data_"$ID"-train_val_nl.ql --output $DICT_DIR/dict-$ID.ql
else
  # rename the train_val files
  for L in nl ql; do
    cat $INT_DIR/data_"$ID"-train_val_nl.$L > $INT_DIR/data_"$ID"-train_val.$L
  done

  echo "Create dictionaries using raw input files..."
  cat $INT_DIR/data_"$ID"-train_val_nl.nl.raw |
    tr -s '[:space:]' '\n' | # turns every space into a \n, so every word into new line; several spaces into single one
    sort |
    uniq -c > $INT_DIR/dict.pg.interim # counts how many duplicate lines there are, returns count before line

    cat $INT_DIR/dict.pg.interim | # $DATA_DIR/dict.iwslt.reversed.en |
    sort -k2 |
    uniq -f 1 | # filter out double elements
    sort -k1,1 -b -n -r -k2 | # sort based on first column, numeric values reversed
    head -n "$((VOCAB_SIZE - 4))" | # display first n elements of file
    awk '{ print $2 " " $1 }' > $DICT_DIR/dict-"$ID".nl

  python subword-nmt/subword_nmt/get_vocab.py \
    --input $INT_DIR/data_"$ID"-train_val_nl.ql.raw --output $DICT_DIR/dict-$ID.ql
fi
rm $INT_DIR/dict.pg.interim

echo 'Splitting data intro train and validation...'
python src/splitter.py \
  --inputPath  $INT_DIR/data_"$ID" \
  --outputPath $INT_DIR/data_"$ID" --split 80

echo 'Generating test data...'
python src/generator.py \
  --templates $DATA_DIR \
  --output $INT_DIR --id "$ID" --type test \
  --graph-data-path $DATA_DIR --folder $TEST_TEMPLATES \
  --input-language en \
  --examples-per-template $EXAMPLES_PER_TEMPLATE

if [ $USE_SUBWORDS = YES ]
  then . src/subword_processing.sh $DICT_DIR/dict-$ID.nl $DICT_DIR/dict-"$ID".ql "$ID"
else
  # Copy files from Interim to Processed directly
  for L in nl ql; do
    for f in train.$L val.$L test_{1..$COUNT_TEST}.$L; do
        echo "copying ${f}..."
        cp -R $INT_DIR/data_"$ID"-$f $OUT_DIR/data_"$ID"-$f
    done
  done
fi

#echo 'Learning alignments using script...'
#. src/learn_alignments.sh $ID

if [ "$COPY" = YES ]; then
  echo 'Copy files to model_input'
  . scripts/copy_model_input.sh "$ID" $ID_SHORT YES NO NO
fi

echo 'Done! Thank you for your patience'
