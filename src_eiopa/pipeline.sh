#!/bin/bash
# full pipeline EIOPA that you can run to prepare the data and train the model

cd ..
echo "Making directories..."
mkdir ./data/eiopa/2_interim/logs
mkdir ./data/eiopa/3_processed/logs
# mkdir ../data/nqm/processed

echo "Generate job ID"
# RANDOM=$(date +%s%N | cut -b10-19)
ID=$(date +"%d-%m_%H-%M")_$RANDOM
echo "Job ID is set at:"
echo $ID

# echo 'Putting the annotations_monument.csv in the interim folder...'
# cp ../data/nqm/external/annotations_monument.csv ../data/nqm/interim

echo 'Generating data (train, validation)...'
python src_eiopa/features/generator.py --templates data/eiopa/1_external/templates.csv --output data/eiopa/2_interim --id $ID --type train_val
echo 'Splitting data intro train and validation...'
python src_eiopa/features/splitter.py --inputPath  data/eiopa/2_interim/data_train_val_$ID --outputPath data/eiopa/3_processed/data_$ID --split 80

echo 'Generating test data...'
python src_eiopa/features/generator.py --templates data/eiopa/1_external/templates_test_1.csv --output data/eiopa/3_processed --id $ID --type test_1
python src_eiopa/features/generator.py --templates data/eiopa/1_external/templates_test_2.csv --output data/eiopa/3_processed --id $ID --type test_2
python src_eiopa/features/generator.py --templates data/eiopa/1_external/templates_test_3.csv --output data/eiopa/3_processed --id $ID --type test_3

# echo 'Making vocabularies...'
# cd ../models
# onmt_build_vocab -config train_config.yaml
#
# echo 'Training model...'
# onmt_train -config train_config.yaml
#
# cd ..

cd src_eiopa
echo 'Done! Thank you for your patience'
