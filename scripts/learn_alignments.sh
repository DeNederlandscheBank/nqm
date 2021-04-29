#!/bin/bash

ID=10578
if [ -n "$1" ]
    then ID=$1
fi

ALIGN=fast_align/build/fast_align
OUT_DIR=data/eiopa/3_processed
DICT_DIR=data/eiopa/4_vocabularies

NL_TRAIN=$OUT_DIR/data_$ID-train.nl
QL_TRAIN=$OUT_DIR/data_$ID-train.ql
MERGED=$OUT_DIR/data_$ID-train.shared
ALIGNMENTS=$DICT_DIR/train_$ID.align

paste $NL_TRAIN $QL_TRAIN | awk -F '\t' '{print $1 " ||| " $2}' > $MERGED
$ALIGN -i $MERGED -d -o -v > $ALIGNMENTS