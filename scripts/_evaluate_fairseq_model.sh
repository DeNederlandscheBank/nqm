#!/bin/bash

ID=1689
IN_DIR=data/eiopa/5_model_input
MODEL_DIR=models/transformer_iwslt_de_en_$ID
OUT_FILE=$MODEL_DIR/out_$ID/translation_test.txt

echo "Generate translations using fairseq-generate"
fairseq-generate $IN_DIR/fairseq-data-bin-$ID \
  --gen-subset test \
  --path $MODEL_DIR/checkpoint_best.pt \
  --results-path $MODEL_DIR/out_$ID \
  --beam 5  \
  --batch-size 128 \
  --scoring bleu \
  --remove-bpe \
  --empty-cache-freq 5

echo "Decode the queries"
python src_eiopa/decode_fairseq_output.py \
  --in-file $MODEL_DIR/out_$ID/generate-test.txt \
  --out-file $OUT_FILE

