#!/bin/bash

DATA_DIR=../data/eiopa/4_dictionaries/fairseq-data-bin-31181
MODEL_DIR=../models/transformer_iwslt_de_en_20226912

fairseq-interactive \
    --path $MODEL_DIR/checkpoint_best.pt $DATA_DIR \
    --beam 5 --source-lang nl --target-lang ql \
    --tokenizer moses \
#    --bpe subword_nmt --bpe-codes $MODEL_DIR/bpecodes