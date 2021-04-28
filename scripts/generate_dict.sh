#!/bin/bash

IN_DIR=data/eiopa/2_interim
OUT_DIR=$IN_DIR
INPUT=$IN_DIR/data_28-04_14-57_349-dev-train_val.ql.raw
DICT_OUT=$OUT_DIR/10578-dev-train_val.ql.dict


python src_eiopa/subword-nmt/subword_nmt/get_vocab.py \
  --input $INPUT --output $DICT_OUT

echo "Find generated dictionary at $DICT_OUT"