#!/bin/bash

ALIGN=fast_align/build/fast_align

NL_TRAIN=data/eiopa/2_interim/data_27-04_15-02_10578-dev-train.nl
QL_TRAIN=data/eiopa/2_interim/data_27-04_15-02_10578-dev-train.ql
MERGED=data/eiopa/2_interim/10578-dev-train.ql-nl
ALIGNMENTS=data/eiopa/2_interim/10578-dev-train.align

paste $NL_TRAIN $QL_TRAIN | awk -F '\t' '{print $1 " ||| " $2}' > $MERGED
$ALIGN -i $MERGED -d -o -v > $ALIGNMENTS