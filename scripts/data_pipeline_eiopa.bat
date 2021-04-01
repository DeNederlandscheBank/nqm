:: full pipeline EIOPA that you can run to prepare the data and train the model

# pipeline is run from root directory of project
echo "Making directories..."
mkdir data\eiopa\3_processed\logs
mkdir data\eiopa\2_interim\logs

# .bat script has no date added for job id, since that is complicated due to locale dependent time format
echo "Generate job id"
set /a num=$random$

set DATA_DIR=data/eiopa/1_external
set OUT_DIR=data/eiopa/3_processed

echo 'Generating data (train, validation)...'
python src_eiopa/features/generator.py --templates %DATA_DIR%/templates.csv --output data/eiopa/2_interim --id %num% --type train_val --graph-data-path %DATA_DIR%

echo 'Splitting data intro train and validation...'
python src_eiopa/features/splitter.py --inputPath  data/eiopa/2_interim/data_%num% --outputPath %OUT_DIR%/data_%num% --split 80

echo 'Generating test data...'
python src_eiopa/features/generator.py --templates %DATA_DIR%/templates_test_1.csv --output %OUT_DIR% --id %num% --type test_1 --graph-data-path %DATA_DIR%
python src_eiopa/features/generator.py --templates %DATA_DIR%/templates_test_2.csv --output %OUT_DIR% --id %num% --type test_2 --graph-data-path %DATA_DIR%
python src_eiopa/features/generator.py --templates %DATA_DIR%/templates_test_3.csv --output %OUT_DIR% --id %num% --type test_3 --graph-data-path %DATA_DIR%

echo 'Done! Thank you for your patience'
