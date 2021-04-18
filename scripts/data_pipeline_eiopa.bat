echo "Making directories..."
mkdir "data/eiopa/2_interim/logs"
mkdir "data/eiopa/3_processed/logs"
mkdir "data/eiopa/4_vocabularies"

set ID=1689
set DATA_DIR=data/eiopa/1_external
set OUT_DIR=data/eiopa/3_processed
set INT_DIR=data/eiopa/2_interim
set DICT_DIR=data/eiopa/4_vocabularies
set TEST_TEMPLATES=test_templates

echo "Generate job ID"
echo "Job ID is set at:"
echo "%ID%"

set BPE_CODE=%DICT_DIR%/%ID%-bpe.codes

echo 'Generating data (train, validation)...'
python src_eiopa/generator.py ^
  --templates %DATA_DIR%/templates.csv ^
  --output %INT_DIR% --id %ID% --type train_val ^
  --graph-data-path %DATA_DIR% --input-language en
echo 'Splitting data intro train and validation...'
python src_eiopa/splitter.py ^
  --inputPath  %INT_DIR%/data_%ID% ^
  --outputPath %INT_DIR%/data_%ID% --split 80

echo 'Generating test data...'
python src_eiopa/generator.py ^
  --templates %DATA_DIR% ^
  --output %INT_DIR% --id %ID% --type test ^
  --graph-data-path %DATA_DIR% --folder %TEST_TEMPLATES% ^
  --input-language en

echo 'Learning BPE codes using subword_nmt'
python src_eiopa/subword-nmt/subword_nmt/learn_joint_bpe_and_vocab.py ^
  --input %INT_DIR%/data_%ID%-train.nl %INT_DIR%/data_%ID%-train.ql ^
  --output %BPE_CODE% ^
  --write-vocabulary %DICT_DIR%/%ID%-vocab.nl %DICT_DIR%/%ID%-vocab.ql ^
  --symbols 50

FOR %%L IN (nl, ql) DO ^
FOR %%f IN (train.%%L, val.%%L, test_1.%%L, test_2.%%L, test_3.%%L) DO ^
python src_eiopa/subword-nmt/subword_nmt/apply_bpe.py ^
  --codes %BPE_CODE% ^
  --input %INT_DIR%/data_%ID%-%%f ^
  --output %OUT_DIR%/data_%ID%-%%f ^
  --vocabulary %DICT_DIR%/%ID%-vocab.%%L

echo 'Done! Thank you for your patience'
