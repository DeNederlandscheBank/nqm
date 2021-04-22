#!/bin/bash

ID=5847
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


for f in test_{1..$COUNT_TEST}; do
  echo "Generate translations using fairseq-generate for $f"
  fairseq-generate $IN_DIR/fairseq-data-bin-$ID \
    --gen-subset $f \
    --path $MODEL_DIR/checkpoint_best.pt \
    --results-path $OUT_DIR \
    --beam 5  \
    --batch-size 128 \
    --scoring bleu \
    --remove-bpe

  echo "Decode the queries for $f"
  python src_eiopa/decode_fairseq_output.py \
    --in-file $MODEL_DIR/out_$ID/generate-$f.txt \
    --out-file $OUT_DIR/decoded-$f.txt \
    --summary-file $OUT_DIR/summary-$ID.txt

  echo "Evaluate query performance"
  python src_eiopa/query_results_evaluation.py \
    --graph-path $DATA_DIR \
    --query-file $OUT_DIR/decoded-$f.txt \
    --out-file $OUT_DIR/queries_and_results-$f.txt \
    --summary-file $OUT_DIR/summary-$ID.txt
done

