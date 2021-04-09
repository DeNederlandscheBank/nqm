#!/bin/bash

DIRECTORY=data/eiopa/4_dictionaries
FILE=$DIRECTORY/data_09-04_16-51_183
ID=183

fairseq-preprocess -s nl -t ql \
  --trainpref $FILE-train --validpref $FILE-val --testpref $FILE-test_1 --testpref $FILE-test_2 \
  --destdir $DIRECTORY/fairseq-data-bin-$ID \
  --bpe subword_nmt --cpu --empty-cache-freq 10
