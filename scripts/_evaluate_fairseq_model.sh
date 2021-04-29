#!/bin/bash
# BROKEN
ID=5861
ID_MODEL=14126

if [ -n "$1" ]
    then ID=$1
fi
if [ -n "$2" ]
    then ID_MODEL=$2
fi

DATA_DIR=data/eiopa/1_external
TEST_TEMPLATES=test_templates
IN_DIR=data/eiopa/5_model_input
MODEL_DIR=models/transformer_iwslt_de_en_$ID_MODEL
OUT_DIR=$MODEL_DIR/out_$ID
COUNT_TEST=$((`ls -l $DATA_DIR/$TEST_TEMPLATES/*.csv | wc -l` ))
DATA_BIN=$IN_DIR/fairseq-data-bin-$ID_MODEL

for f in test.nl-ql.nl ; do #..$COUNT_TEST}; do
  fairseq-generate $IN_DIR/fairseq-data-bin-$ID_MODEL \
    --gen-subset $f \
    --path $MODEL_DIR/checkpoint_best.pt \
    --results-path $OUT_DIR \
    --beam 5  \
    --batch-size 128 \
    --scoring bleu \
    --remove-bpe \
    --replace-unk --dataset-impl raw
done

#mkdir -p $OUT_DIR
##for f in test_{1..$COUNT_TEST}; do
##for f in nl ql; do
##  echo "Generate translations using fairseq-generate for $f"
#for f in test_{1..$COUNT_TEST}.nl; do
#  echo "Generate translations using fairseq-generate for $f"
#  cat $IN_DIR/data_$ID-$f | \
#    fairseq-interactive $DATA_BIN \
#      --path $MODEL_DIR/checkpoint_best.pt  \
#      --beam 5 --source-lang nl --target-lang ql \
#      --print-alignment --replace-unk \
#      --tokenizer moses \
#    > $OUT_DIR/generate-$f.txt
#
#  echo "Decode the queries for $f"
#  python src_eiopa/decode_fairseq_output.py \
#    --in-file $MODEL_DIR/out_$ID/generate-$f.txt \
#    --out-file $OUT_DIR/decoded-$f.txt \
#    --summary-file $OUT_DIR/summary-$ID.txt
#
#  echo "Evaluate query performance"
#  python src_eiopa/query_results_evaluation.py \
#    --graph-path $DATA_DIR \
#    --query-file $OUT_DIR/decoded-$f.txt \
#    --out-file $OUT_DIR/queries_and_results-$f.txt \
#    --summary-file $OUT_DIR/summary-$ID.txt
#done

