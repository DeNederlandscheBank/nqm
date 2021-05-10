#!/bin/bash

# This script should be run from root and can be used to check the translation of a particular sentence.

ID=5861
ID_MODEL=$ID

MODEL_DIR=models/transformer_iwslt_de_en_$ID_MODEL
IN_DIR=data/eiopa/5_model_input
DATA_BIN=$IN_DIR/fairseq-data-bin-$ID
BPECODES=$IN_DIR/$ID-bpe.codes

CHECKPOINT_BEST_BLEU=$(find $MODEL_DIR -name 'checkpoint.best_bleu_*.pt')


fairseq-interactive $DATA_BIN \
    --path $CHECKPOINT_BEST_BLEU  \
    --beam 5 --source-lang nl --target-lang ql \
    --tokenizer moses \
    --print-alignment --replace-unk \
#    --bpe subword_nmt --bpe-codes $BPECODES \
