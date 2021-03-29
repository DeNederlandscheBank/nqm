#!/bin/bash

PATH=../../data/eiopa/4_dictionaries
FILE=$PATH/data_24-03_14-14_31181

/Users/jan_marcglowienke/anaconda3/envs/nqm_torch/bin/fairseq-preprocess -s nl -t ql --trainpref $FILE-train --validpref $FILE-val --testpref $FILE-test_1 --destdir $PATH/fairseq-data-bin --joined-dictionary
