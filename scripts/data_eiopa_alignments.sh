#!/bin/bash
# full pipeline EIOPA that you can run to prepare the data and train the model
# Use this script from the root!

USE_SUBWORDS=NO # use of subword splitting
CREATE_SUBWORD_DICTIONARY=NO # generate dictionary using subword split sentences

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

echo "Generate job ID"
# RANDOM=$(date +%s%N | cut -b10-19)
ID=$(date +"%d-%m_%H-%M")_$RANDOM
echo "Job ID is set at:"
echo "$ID"

echo 'Generating data (train, validation)...'
python src_eiopa/generator.py \
  --templates $DATA_DIR/templates_newnames.csv \
  --output $INT_DIR --id "$ID" --type train_val \
  --graph-data-path $DATA_DIR --input-language en
echo 'Splitting data intro train and validation...'
python src_eiopa/splitter.py \
  --inputPath  $INT_DIR/data_"$ID" \
  --outputPath $INT_DIR/data_"$ID" --split 80

echo 'Generating test data...'
python src_eiopa/generator.py \
  --templates $DATA_DIR \
  --output $INT_DIR --id "$ID" --type test \
  --graph-data-path $DATA_DIR --folder $TEST_TEMPLATES \
  --input-language en

#echo 'Generate SPARQL dictionary...'
#python src_eiopa/subword-nmt/subword_nmt/get_vocab.py \
#  --input $INT_DIR/data_$ID-train_val.ql.raw --output $DICT_DIR/dict-$ID.ql

echo 'Generate dictionaries with names included..'
for L in nl ql; do
  python src_eiopa/subword-nmt/subword_nmt/get_vocab.py \
    --input $INT_DIR/data_$ID-train.$L --output $DICT_DIR/dict-$ID.$L
done

if [ $USE_SUBWORDS = YES ]
  then . scripts/subword_processing.sh $DICT_DIR/dict-$ID.ql $CREATE_SUBWORD_DICTIONARY $ID
else
  # Copy files from Interim to Processed directly
  for L in nl ql; do
    for f in train.$L val.$L test_{1..$COUNT_TEST}.$L; do
        echo "copying ${f}..."
        cp -R $INT_DIR/data_"$ID"-$f $OUT_DIR/data_"$ID"-$f
    done
  done
fi

echo 'Learning alignments using script...'
. scripts/learn_alignments.sh $ID


echo 'Done! Thank you for your patience'
