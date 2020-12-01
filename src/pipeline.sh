# full pipeline that you can run to prepare the data and train the model

echo "Making directories..."
mkdir ../data/interim
mkdir ../data/processed

echo 'Putting the annotations_monument.csv in the interim folder...'
cp ../data/external/annotations_monument.csv ../data/interim

echo 'Generating data (train, test, dev)...'
cd ..
python src/features/generator.py --templates data/interim/annotations_monument.csv --output data/processed
python src/features/split_in_train_dev_test.py --dataset data/processed/data

echo 'Shuffling data...'
cd src/features
python shuffle.py

echo 'Making vocabularies...'
cd ../models
onmt_build_vocab -config train_config.yaml

echo 'Training model...'
onmt_train -config train_config.yaml

echo 'Done! Thank you for your patience'
