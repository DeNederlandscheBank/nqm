#!/bin/bash

ID=1689
DATA_DIR=data/eiopa/5_model_input
MODEL_DIR=models/transformer_iwslt_de_en
OUT_FILE=$MODEL_DIR/out_$ID/translation_test.txt

echo "Generate translations using fairseq-generate"
fairseq-generate $DATA_DIR/fairseq-data-bin-$ID \
  --gen-subset test \
  --path $MODEL_DIR/checkpoint_best.pt \
  --results-path $MODEL_DIR/out_$ID \
  --beam 5  \
  --batch-size 128 \
  --scoring bleu \
  --remove-bpe

echo "Decode the queries"
python src_eiopa/evaluation/decode_fairseq_output.py \
  --in-file $MODEL_DIR/out_$ID/generate-test.txt \
  --out-file $OUT_FILE

