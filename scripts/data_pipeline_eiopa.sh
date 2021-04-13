#!/bin/bash
# full pipeline EIOPA that you can run to prepare the data and train the model
# Use this script from the root!

echo "Making directories..."
mkdir -p ./data/eiopa/2_interim/logs
mkdir -p ./data/eiopa/3_processed/logs
mkdir -p ./data/eiopa/4_vocabularies
# mkdir ../data/nqm/processed

DATA_DIR=data/eiopa/1_external # input data location
OUT_DIR=data/eiopa/3_processed
INT_DIR=data/eiopa/2_interim
DICT_DIR=data/eiopa/4_vocabularies
TEST_TEMPLATES=test_templates

echo "Generate job ID"
# RANDOM=$(date +%s%N | cut -b10-19)
ID=$(date +"%d-%m_%H-%M")_$RANDOM
echo "Job ID is set at:"
echo "$ID"

BPE_CODE=$DICT_DIR/$ID-bpe.codes

echo 'Generating data (train, validation)...'
python src_eiopa/features/generator.py \
  --templates $DATA_DIR/templates.csv \
  --output $INT_DIR --id "$ID" --type train_val \
  --graph-data-path $DATA_DIR --input-language en
echo 'Splitting data intro train and validation...'
python src_eiopa/features/splitter.py \
  --inputPath  $INT_DIR/data_"$ID" \
  --outputPath $INT_DIR/data_"$ID" --split 80

echo 'Generating test data...'
python src_eiopa/features/generator.py \
  --templates $DATA_DIR \
  --output $INT_DIR --id "$ID" --type test \
  --graph-data-path $DATA_DIR --folder $TEST_TEMPLATES \
  --input-language en

echo 'Learning BPE codes using subword_nmt'
python src_eiopa/subword-nmt/subword_nmt/learn_joint_bpe_and_vocab.py \
  --input $INT_DIR/data_"$ID"-train.nl $INT_DIR/data_"$ID"-train.ql \
  --output $BPE_CODE \
  --write-vocabulary $DICT_DIR/$ID-vocab.nl $DICT_DIR/$ID-vocab.ql \
  --symbols 50

COUNT_TEST=$((`ls -l $DATA_DIR/$TEST_TEMPLATES | wc -l` -1 ))

# Apply bpe to all relevant files
for L in nl ql; do # both languages
    for f in train.$L val.$L test_{1..$COUNT_TEST}.$L; do
        echo "apply_bpe.py to ${f}..."
        python src_eiopa/subword-nmt/subword_nmt/apply_bpe.py \
        --codes "$BPE_CODE" \
        --input $INT_DIR/data_"$ID"-$f \
        --output $OUT_DIR/data_"$ID"-$f \
        --vocabulary $DICT_DIR/$ID-vocab.$L
    done
done

echo 'Done! Thank you for your patience'
