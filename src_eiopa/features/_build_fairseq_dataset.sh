#!/bin/bash

PATH=../../data/eiopa/4_dictionaries/data_24-03_14-14_31181

fairseq-preprocess -s en -t sparql --trainpref $PATH-train --validpref $PATH-dev --testpref $PATH-test_1 --destdir $PATH/fairseq-data-bin --joined-dictionary
