#!/bin/bash
# full pipeline EIOPA that you can run to prepare the data and train the model for the XLMR model
# Use this script from the root!

COPY=YES # set this variable to YES, if the generated files should be directly copied to the model_input folder
USE_SENTENCEPIECE=YES # use of subword splitting, in this script using sentencepiece package
BILINGUAL=YES
USE_KNOWN_AND_UNKNOWN_NAMES=NO
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
    --graph-data-path $DATA_DIR --input-language nl\
    --examples-per-template $EXAMPLES_PER_TEMPLATE
fi


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

if [ $USE_SENTENCEPIECE = YES ]; then
  for L in nl ql; do
    for f in train.$L val.$L test_{1..$COUNT_TEST}.$L; do
        echo "sentencepiece pre-process ${f}..."
        python src/sentencepiece_processing.py \
          --preprocess-file \
          --in-file $INT_DIR/data_"$ID"-$f \
          --out-file $OUT_DIR/data_"$ID"-$f \
          --model $DATA_DIR/sentencepiece.bpe.xlmr.model
    done
  done
  echo "Get .ql dictionary"
  python src/sentencepiece_processing.py \
          --preprocess-file \
          --in-file $INT_DIR/data_"$ID"-train_val.ql \
          --out-file $INT_DIR/data_"$ID"-train_val.ql.bpe \
          --model $DATA_DIR/sentencepiece.bpe.xlmr.model
  python subword-nmt/subword_nmt/get_vocab.py \
    --input $INT_DIR/data_"$ID"-train_val.ql.bpe --output $DICT_DIR/dict-$ID.ql
else
  # Copy files from Interim to Processed directly
  for L in nl ql; do
    for f in train.$L val.$L test_{1..$COUNT_TEST}.$L; do
        echo "copying ${f}..."
        cp -R $INT_DIR/data_"$ID"-$f $OUT_DIR/data_"$ID"-$f
    done
  done
fi


if [ "$COPY" = YES ]; then
  echo 'Copy files to model_input'
  . scripts/copy_model_input.sh "$ID" $ID_SHORT YES NO YES
fi

echo 'Done! Thank you for your patience'
