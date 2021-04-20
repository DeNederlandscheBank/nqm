#!/bin/bash

# Use this script from the root!
# Similiar to before, the ID variable needs to be corrected to the correct value.
ID=1689
DIRECTORY=data/eiopa/5_model_input
DATA_DIR=data/eiopa/1_external
TEST_TEMPLATES=test_templates
COUNT_TEST=$((`ls -l $DATA_DIR/$TEST_TEMPLATES/*.csv | wc -l` ))
FILE=$DIRECTORY/data_$ID
OUT_DIR=data/eiopa/5_model_input
DATA_BIN=$OUT_DIR/fairseq-data-bin-$ID


fairseq-preprocess -s nl -t ql \
  --trainpref $FILE-train --validpref $FILE-val \
  --destdir $DATA_BIN \
  --cpu --empty-cache-freq 10

for f in test_{1..$COUNT_TEST}; do
  # Create multiple files using dictionary from above
  # this goes into different folders due to fairseq
  fairseq-preprocess -s nl -t ql \
    --testpref $FILE-$f \
    --destdir $DATA_BIN-$f \
    --cpu --empty-cache-freq 10 \
    --srcdict $DATA_BIN/dict.nl.txt \
    --tgtdict $DATA_BIN/dict.ql.txt
  # collect all test files in one folder and rename them
  for L in nl ql; do
    for S in bin idx; do
      echo "Copying $f.nl-ql.$L.$S"
      cp -R $DATA_BIN-$f/test.nl-ql.$L.$S \
       $DATA_BIN/$f.nl-ql.$L.$S
    done
  done
  echo "Deleting folder $DATA_BIN-$f/"
  rm -R $DATA_BIN-$f/
  done
