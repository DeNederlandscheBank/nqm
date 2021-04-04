#!/bin/bash
# full pipeline EIOPA that you can run to prepare the data and train the model
# this script should be run from the root

echo "Making directories..."
mkdir -p ./data/eiopa/2_interim/logs
mkdir -p ./data/eiopa/3_processed/logs
# mkdir ../data/nqm/processed

DATA_DIR=data/eiopa/1_external # input data location
OUT_DIR=data/eiopa/3_processed

echo "Generate job ID"
# RANDOM=$(date +%s%N | cut -b10-19)
ID=$(date +"%d-%m_%H-%M")_$RANDOM
echo "Job ID is set at:"
echo $ID

# echo 'Putting the annotations_monument.csv in the interim folder...'
# cp ../data/nqm/external/annotations_monument.csv ../data/nqm/interim

echo 'Generating data (train, validation)...'
python src_eiopa/features/generator.py \
  --templates $DATA_DIR/templates.csv \
  --output data/eiopa/2_interim --id $ID --type train_val \
  --graph-data-path $DATA_DIR
echo 'Splitting data intro train and validation...'
python src_eiopa/features/splitter.py \
  --inputPath  data/eiopa/2_interim/data_$ID \
  --outputPath $OUT_DIR/data_$ID --split 80

echo 'Generating test data...'
python src_eiopa/features/generator.py \
  --templates $DATA_DIR \
  --output $OUT_DIR --id $ID --type test \
  --graph-data-path $DATA_DIR --folder test_templates

echo 'Done! Thank you for your patience'
