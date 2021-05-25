#!/bin/zsh
# full pipeline EIOPA that you can run to prepare the data and train the model
# TO BE USED FOR THE POINTER-GENERATOR MODEL
# Use this script from the root!

USE_KNOWN_AND_UNKNOWN_NAMES=NO # if NO, all names are treated as unknown

VOCAB_SIZE=15000
POSITION_MARKERS=100

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

echo "Generate job ID"
# RANDOM=$(date +%s%N | cut -b10-19)
ID=$(date +"%d-%m_%H-%M")_$RANDOM
echo "Job ID is set at:"
echo "$ID"

# reverse columns of dict.iwslt.en
cat $DATA_DIR/dict.iwslt.en |
    awk '{ print $2 " " $1 }' >$DATA_DIR/dict.iwslt.reversed.en

echo 'Generating data (train, validation) for NL insurers...'
python src_eiopa/generator.py \
  --templates $DATA_DIR/templates.csv \
  --output $INT_DIR --id "$ID" --type train_val_nl \
  --graph-data-path $DATA_DIR --input-language en

if [ $USE_KNOWN_AND_UNKNOWN_NAMES = "YES" ]; then
  echo 'Generating data (train, validation) for DE insurers...'
  python src_eiopa/generator.py \
    --templates $DATA_DIR/templates_DE.csv \
    --output $INT_DIR --id "$ID" --type train_val_de \
    --graph-data-path $DATA_DIR --input-language en

  echo "Concatenate files with NL and DE insurance names..."
  for L in nl ql; do
    cat $INT_DIR/data_"$ID"-train_val_nl.$L $INT_DIR/data_"$ID"-train_val_de.$L > $INT_DIR/data_"$ID"-train_val.$L
  done

  echo "Create shared dictionary and add position markers for OOV words..."
  cat $INT_DIR/data_"$ID"-train_val_nl.nl $INT_DIR/data_"$ID"-train_val_nl.ql |
    tr -s '[:space:]' '\n' | # turns every space into a \n, so every word into new line; several spaces into single one
    sort |
    uniq -c > $INT_DIR/dict.pg.interim # counts how many duplicate lines there are, returns count before line

    cat $INT_DIR/dict.pg.interim $DATA_DIR/dict.iwslt.reversed.en |
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

    cat $INT_DIR/dict.pg.interim $DATA_DIR/dict.iwslt.reversed.en |
    sort -k2 |
    uniq -f 1 | # filter out double elements
    sort -k1,1 -b -n -r -k2 | # sort based on first column, numeric values reversed
    head -n "$((VOCAB_SIZE - 4))" | # display first n elements of file
    awk '{ print $2 " " $1 }' > $DICT_DIR/dict."$ID".shared
  python3 -c "[print('<unk-{}> 0'.format(n)) for n in range($POSITION_MARKERS)]" >> $DICT_DIR/dict."$ID".shared
fi

echo 'Splitting data intro train and validation...'
python src_eiopa/splitter.py \
  --inputPath $INT_DIR/data_"$ID" \
  --outputPath $INT_DIR/data_"$ID" --split 80

echo 'Generating test data...'
python src_eiopa/generator.py \
  --templates $DATA_DIR \
  --output $INT_DIR --id "$ID" --type test \
  --graph-data-path $DATA_DIR --folder $TEST_TEMPLATES \
  --input-language en

echo "Preprocess using pointer-generator preprocess.py..."
  for f in train val test_{1..$COUNT_TEST}; do
    python src_eiopa/pg_preprocess.py \
      --source $INT_DIR/data_"$ID"-$f.nl \
      --target $INT_DIR/data_"$ID"-$f.ql \
      --vocab $DICT_DIR/dict."$ID".shared \
      --source-out $OUT_DIR/data_"$ID"-$f.nl \
      --target-out $OUT_DIR/data_"$ID"-$f.ql
  done

echo "Copy shared dict to nl and ql dict for building fairseq dataset..."
  cat $DICT_DIR/dict."$ID".shared > $DICT_DIR/dict-"$ID".nl
  cat $DICT_DIR/dict."$ID".shared > $DICT_DIR/dict-"$ID".ql

echo 'Learning alignments using script...'
. scripts/learn_alignments.sh $ID

echo 'Done! Thank you for your patience'
