#!/bin/bash

ID=30101 # find in build script or end of fairseq-data-bin

if [ -n "$1" ]
    then ID=$1
fi

IN_DIR=data/eiopa/5_model_input
MODEL_DIR=models/test_run_$ID
OUT_DIR=$MODEL_DIR/out_$ID # output directory for model
WORK_DIR=.

#fairseq-train $IN_DIR/fairseq-data-bin-$ID \
#  -a transformer_pointer_generator_iwslt_de_en --optimizer adam --lr 0.0005 -s nl -t ql \
#  --tensorboard-logdir $MODEL_DIR/out_$ID/ \
#  --label-smoothing 0.1 --dropout 0.3 --max-tokens 4000 \
#  --lr-scheduler inverse_sqrt --weight-decay 0.0001 \
#  --criterion label_smoothed_cross_entropy --scoring bleu \
#  --warmup-updates 4000 --warmup-init-lr '1e-07' \
#  --max-epoch 1 --save-interval 1 --valid-subset valid \
#  --adam-betas '(0.9, 0.98)' --save-dir $MODEL_DIR \
#  --batch-size 128 --keep-best-checkpoints 1 --patience 50 \
#  --eval-bleu \
#    --eval-bleu-args '{"beam": 5, "max_len_a": 1.2, "max_len_b": 10}' \
#    --eval-bleu-detok space \
#    --eval-bleu-remove-bpe \
#    --best-checkpoint-metric bleu --maximize-best-checkpoint-metric \
#  --source-position-markers 100 --alignment-layer 1 \
#  --alignment-heads 1

#fairseq-train $IN_DIR/fairseq-data-bin-$ID \
#    --arch transformer_pointer_generator_iwslt_de_en \
#    --optimizer adam --adam-betas "(0.9, 0.98)" --adam-eps 1e-08 \
#    -s nl -t ql \
#    --tensorboard-logdir $MODEL_DIR/out_$ID/ \
#    --label-smoothing 0.1 --dropout 0.3 --max-tokens 4000 \
#    --attention-dropout 0.1 --clip-norm 0.1  --update-freq 4 \
#    --lr-scheduler inverse_sqrt --weight-decay 0.01 --lr 0.001  \
#    --criterion label_smoothed_cross_entropy --scoring bleu \
#    --warmup-updates 4000 --warmup-init-lr '1e-07' \
#    --max-epoch 1 --save-interval 1 --valid-subset valid \
#    --save-dir $MODEL_DIR \
#    --batch-size 128 --keep-best-checkpoints 1 --patience 50 \
#    --task translation \
#    --truncate-source --layernorm-embedding --share-all-embeddings \
#    --encoder-normalize-before --decoder-normalize-before \
#    --required-batch-size-multiple 1 --skip-invalid-size-inputs-valid-test \
#    --alignment-layer -2 --alignment-heads 1 --source-position-markers 1000 \
#    --eval-bleu \
#      --eval-bleu-args '{"beam": 5, "max_len_a": 1.2, "max_len_b": 10}' \
#      --eval-bleu-detok space \
#      --eval-bleu-remove-bpe \
#      --best-checkpoint-metric bleu --maximize-best-checkpoint-metric

fairseq-train $IN_DIR/fairseq-data-bin-$ID \
  --pretrained-xlm-checkpoint $WORK_DIR/models/xlmr.base/model.pt --task translation_from_pretrained_xlm \
  --encoder-learned-pos --decoder-learned-pos --max-source-positions 512 \
  --arch transformer_xlm_iwslt_decoder --optimizer adam --lr 0.0005 -s nl -t ql \
  --label-smoothing 0.1 --dropout 0.3 --max-tokens 4000 \
  --lr-scheduler inverse_sqrt --weight-decay 0.0001 \
  --criterion label_smoothed_cross_entropy --scoring bleu \
  --warmup-updates 4000 --warmup-init-lr '1e-07' \
  --max-epoch 200 --save-interval 30 --valid-subset valid \
  --adam-betas '(0.9, 0.98)' --save-dir $MODEL_DIR \
  --batch-size 256 --keep-best-checkpoints 1 --patience 20 \
  --eval-bleu \
  --eval-bleu-args '{"beam": 5, "max_len_a": 1.2, "max_len_b": 10}' \
  --eval-bleu-detok space \
  --eval-bleu-remove-bpe \
  --best-checkpoint-metric bleu --maximize-best-checkpoint-metric \
  --stop-time-hours 12 --cpu  \
  --tensorboard-logdir $OUT_DIR












