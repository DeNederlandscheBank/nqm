:: full pipeline EIOPA that you can run to prepare the data and train the model

cd ..
echo "Making directories..."
mkdir .\data\eiopa\3_processed\logs

echo "Generate job id"
:: .bat script has no date added for job id, since that is complicated due to locale dependent time format
set /a num=$random$

echo 'Generating data (train, test, dev)...'
cd ..
python ./src_eiopa/features/generator.py --templates data/eiopa/1_external/templates.csv --output data/eiopa/3_processed --id %num%

:: echo 'Shuffling data...'
:: cd src/features
:: python shuffle.py

:: echo 'Making vocabularies...'
:: cd ../models
:: onmt_build_vocab -config train_config.yaml

:: echo 'Training model...'
:: onmt_train -config train_config.yaml


echo 'Done! Thank you for your patience'
