:: full pipeline EIOPA that you can run to prepare the data and train the model

cd ..
echo "Making directories..."
mkdir data\eiopa\3_processed\logs
mkdir data\eiopa\2_interim\logs

echo "Generate job id"
:: .bat script has no date added for job id, since that is complicated due to locale dependent time format
set /a num=$random$

echo 'Generating data (train, validation)...'
python src_eiopa/features/generator.py --templates data/eiopa/1_external/templates.csv --output data/eiopa/3_processed --id %num%
echo 'Splitting data intro train and validation...'
python src_eiopa/features/splitter.py --inputPath  data/eiopa/2_interim/data_train_val_%num% --outputPath data/eiopa/3_processed/data_%num% --split 80

echo 'Generating test data...'
python src_eiopa/features/generator.py --templates data/eiopa/1_external/templates_test_1.csv --output data/eiopa/3_processed --id %num% --type test_1
python src_eiopa/features/generator.py --templates data/eiopa/1_external/templates_test_2.csv --output data/eiopa/3_processed --id %num% --type test_2
python src_eiopa/features/generator.py --templates data/eiopa/1_external/templates_test_3.csv --output data/eiopa/3_processed --id %num% --type test_3

:: echo 'Making vocabularies...'
:: cd ../models
:: onmt_build_vocab -config train_config.yaml

:: echo 'Training model...'
:: onmt_train -config train_config.yaml


echo 'Done! Thank you for your patience'
