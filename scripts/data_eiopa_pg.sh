#!/bin/zsh
# full pipeline EIOPA that you can run to prepare the data and train the model
# TO BE USED FOR THE POINTER-GENERATOR MODEL
# Use this script from the root!

COPY=NO # set this variable to YES, if the generated files should be directly copied to the model_input folder
USE_KNOWN_AND_UNKNOWN_NAMES=NO # if NO, all names are treated as unknown
BILINGUAL=YES
VOCAB_SIZE=15000
POSITION_MARKERS=100
EXAMPLES_PER_TEMPLATE=130

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
COUNT_TEST=$(($(ls -l $DATA_DIR/$TEST_TEMPLATES/*.csv | wc -l)))
if [ $BILINGUAL = "YES" ]; then
  COUNT_TEST=$((2*COUNT_TEST))
  TEST_TEMPLATES=$TEST_TEMPLATES,"$TEST_TEMPLATES"_dutch
fi

echo "Generate job ID"
ID_SHORT=$RANDOM
ID=$(date +"%d-%m_%H-%M")_"$ID_SHORT"
echo "Job ID is set at:"
echo "$ID"

# reverse columns of dict.iwslt.en
cat $DATA_DIR/dict.iwslt.en |
    awk '{ print $2 " " $1 }' >$DATA_DIR/dict.iwslt.reversed.en

echo 'Generating data (train, validation) for NL insurers...'
python src/generator.py \
  --templates $DATA_DIR/templates.csv \
  --output $INT_DIR --id "$ID" --type train_val_nl \
  --graph-data-path $DATA_DIR --input-language en \
  --examples-per-template $EXAMPLES_PER_TEMPLATE

if [ $BILINGUAL = "YES" ]; then
  echo 'Generating dutch data (train, validation)...'
  # since we use append mode in the generator for writing files, we
  # can directly append the dutch templates on the train_val set
  python src/generator.py \
    --templates $DATA_DIR/templates_dutch.csv \
    --output $INT_DIR --id "$ID" --type train_val_nl \
    --graph-data-path $DATA_DIR --input-language nl\
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

  echo "Create shared dictionary and add position markers for OOV words..."
  cat $INT_DIR/data_"$ID"-train_val_nl.nl $INT_DIR/data_"$ID"-train_val_nl.ql |
    tr -s '[:space:]' '\n' | # turns every space into a \n, so every word into new line; several spaces into single one
    sort |
    uniq -c > $INT_DIR/dict.pg.interim # counts how many duplicate lines there are, returns count before line

    cat $INT_DIR/dict.pg.interim | # $DATA_DIR/dict.iwslt.reversed.en |
    sort -k2 |
    uniq -f 1 | # filter out double elements
    sort -k1,1 -b -n -r -k2 | # sort based on first column, numeric values reversed
    head -n "$((VOCAB_SIZE - 4))" | # display first n elements of file
    awk '{ print $2 " " $1 }' > $DICT_DIR/dict."$ID".shared
  python3 -c "[print('<unk-{}> 0'.format(n)) for n in range($POSITION_MARKERS)]" >> $DICT_DIR/dict."$ID".shared
else
  # rename the train_val files
  for L in nl ql; do
    cat $INT_DIR/data_"$ID"-train_val_nl.$L > $INT_DIR/data_"$ID"-train_val.$L
  done

  echo "Create shared dictionary and add position markers for OOV words using raw input files..."
  cat $INT_DIR/data_"$ID"-train_val_nl.nl.raw $INT_DIR/data_"$ID"-train_val_nl.ql.raw |
    tr -s '[:space:]' '\n' | # turns every space into a \n, so every word into new line; several spaces into single one
    sort |
    uniq -c > $INT_DIR/dict.pg.interim # counts how many duplicate lines there are, returns count before line

    cat $INT_DIR/dict.pg.interim | #$DATA_DIR/dict.iwslt.reversed.en |
    sort -k2 |
    uniq -f 1 | # filter out double elements
    sort -k1,1 -b -n -r -k2 | # sort based on first column, numeric values reversed
    head -n "$((VOCAB_SIZE - 4))" | # display first n elements of file
    awk '{ print $2 " " $1 }' > $DICT_DIR/dict."$ID".shared
  python3 -c "[print('<unk-{}> 0'.format(n)) for n in range($POSITION_MARKERS)]" >> $DICT_DIR/dict."$ID".shared
fi
rm $INT_DIR/dict.pg.interim

echo 'Splitting data intro train and validation...'
python src/splitter.py \
  --inputPath $INT_DIR/data_"$ID" \
  --outputPath $INT_DIR/data_"$ID" --split 80

echo 'Generating test data...'
python src/generator.py \
  --templates $DATA_DIR \
  --output $INT_DIR --id "$ID" --type test \
  --graph-data-path $DATA_DIR --folder $TEST_TEMPLATES \
  --input-language en --examples-per-template $EXAMPLES_PER_TEMPLATE

echo "Preprocess using pointer-generator preprocess.py..."
  for f in train val test_{1..$COUNT_TEST}; do
    python src/pg_preprocess.py \
      --source $INT_DIR/data_"$ID"-$f.nl \
      --target $INT_DIR/data_"$ID"-$f.ql \
      --vocab $DICT_DIR/dict."$ID".shared \
      --source-out $OUT_DIR/data_"$ID"-$f.nl \
      --target-out $OUT_DIR/data_"$ID"-$f.ql
  done

echo "Copy shared dict to nl and ql dict for building fairseq dataset..."
  cat $DICT_DIR/dict."$ID".shared > $DICT_DIR/dict-"$ID".nl
  cat $DICT_DIR/dict."$ID".shared > $DICT_DIR/dict-"$ID".ql

#echo 'Learning alignments using script...'
#. src/learn_alignments.sh $ID

if [ "$COPY" = YES ]; then
  echo 'Copy files to model_input'
  . scripts/copy_model_input.sh "$ID" $ID_SHORT NO YES NO
fi

echo 'Done! Thank you for your patience'
