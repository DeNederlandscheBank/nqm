#!/bin/bash

# Use this script from the root!
# Similiar to before, the ID variable needs to be corrected to the correct value.
ID=14126
DIRECTORY=data/eiopa/5_model_input
#COUNT_TEST=$((`ls -l data/eiopa/1_external/test_templates | wc -l` -1 ))
FILE=$DIRECTORY/data_$ID
OUT_DIR=data/eiopa/5_model_input


fairseq-preprocess -s nl -t ql \
  --trainpref $FILE-train --validpref $FILE-val --testpref $FILE-test_1 \
  --destdir $OUT_DIR/fairseq-data-bin-$ID \
  --cpu --empty-cache-freq 10
