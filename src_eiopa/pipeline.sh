#!/bin/bash
# full pipeline EIOPA that you can run to prepare the data and train the model

cd ..
echo "Making directories..."
mkdir /data/eiopa/3_processed/logs
# mkdir ../data/nqm/processed

echo "Generate job ID"
# RANDOM=$(date +%s%N | cut -b10-19)
ID=$(date +"%d-%m_%H-%M")_$RANDOM
echo "Job ID is set at:"
echo $ID

# echo 'Putting the annotations_monument.csv in the interim folder...'
# cp ../data/nqm/external/annotations_monument.csv ../data/nqm/interim

echo 'Generating data (train, test, dev)...'
python src_eiopa/features/generator.py --templates data/eiopa/1_external/templates.csv --output data/eiopa/3_processed --id $ID
# python src_eiopa/features/split_in_train_dev_test.py --dataset data/nqm/processed/data
#
# echo 'Shuffling data...'
# cd src/features
# python shuffle.py
#
# echo 'Making vocabularies...'
# cd ../models
# onmt_build_vocab -config train_config.yaml
#
# echo 'Training model...'
# onmt_train -config train_config.yaml
#
# cd ..

echo 'Done! Thank you for your patience'
