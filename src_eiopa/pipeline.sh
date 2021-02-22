# full pipeline that you can run to prepare the data and train the model

echo "Making directories..."
mkdir ../data/nqm/interim
mkdir ../data/nqm/processed

echo 'Putting the annotations_monument.csv in the interim folder...'
cp ../data/nqm/external/annotations_monument.csv ../data/nqm/interim

echo 'Generating data (train, test, dev)...'
cd ..
python src/features/generator.py --templates data/nqm/interim/annotations_monument.csv --output data/nqm/processed
python src/features/split_in_train_dev_test.py --dataset data/nqm/processed/data

echo 'Shuffling data...'
cd src/features
python shuffle.py

echo 'Making vocabularies...'
cd ../models
onmt_build_vocab -config train_config.yaml

echo 'Training model...'
onmt_train -config train_config.yaml

cd ..

echo 'Done! Thank you for your patience'
