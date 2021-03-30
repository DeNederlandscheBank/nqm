#!/bin/bash

DIRECTORY=../../data/eiopa/4_dictionaries
FILE=$DIRECTORY/data_24-03_14-14_31181

fairseq-preprocess -s nl -t ql --trainpref $FILE-train --validpref $FILE-val --testpref $FILE-test_1 --destdir $DIRECTORY/fairseq-data-bin
