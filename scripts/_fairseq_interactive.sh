#!/bin/bash

# This script should be run from root and can be used to check the translation of a particular sentence.

ID=30101
ID_MODEL=INDIA

MODEL_DIR=models/$ID_MODEL
IN_DIR=data/eiopa/5_model_input
DATA_BIN=$IN_DIR/fairseq-data-bin-$ID
#BPECODES=$IN_DIR/data_$ID/$ID-bpe.codes
#BPECODES=$IN_DIR/$ID-bpe.codes

CHECKPOINT_BEST_BLEU=$(find $MODEL_DIR -name 'checkpoint.best_bleu_*.pt')

# XLMR model
fairseq-interactive $DATA_BIN \
    --path $CHECKPOINT_BEST_BLEU  \
    --beam 5 --source-lang nl --target-lang ql \
    --tokenizer moses \
    --print-alignment --replace-unk \
    --bpe sentencepiece \
    --task translation_from_pretrained_xlm
    --sentencepiece-model data/eiopa/1_external/sentencepiece.bpe.xlmr.model \
    --model-overrides "{'pretrained_xlm_checkpoint':'interactive'}"