#!/bin/bash

DATA_DIR=data/eiopa/5_model_input/fairseq-data-bin-1689
MODEL_DIR=models/transformer_iwslt_de_en

fairseq-interactive \
    --path $MODEL_DIR/checkpoint_best.pt $DATA_DIR \
    --beam 5 --source-lang nl --target-lang ql \
    --tokenizer moses \
    --bpe subword_nmt --bpe-codes data/eiopa/4_vocabularies/13-04_18-21_1689-bpe.codes