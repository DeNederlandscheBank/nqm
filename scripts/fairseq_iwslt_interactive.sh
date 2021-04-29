#!/bin/bash

DATA_DIR=data/eiopa/5_model_input/fairseq-data-bin-14126
MODEL_DIR=models/transformer_iwslt_de_en_14126

fairseq-interactive \
    --path $MODEL_DIR/checkpoint.best_bleu_81.91.pt $DATA_DIR \
    --beam 5 --source-lang nl --target-lang ql \
    --print-alignment --replace-unk \
    --tokenizer moses \
    --bpe subword_nmt --bpe-codes data/eiopa/4_vocabularies/20-04_10-53_14126-bpe.codes