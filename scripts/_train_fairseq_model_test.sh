#!/bin/bash

ID=7633 # find in build script or end of fairseq-data-bin

if [ -n "$1" ]
    then ID=$1
fi

IN_DIR=data/eiopa/5_model_input
MODEL_DIR=models/test_run_$ID
OUT_DIR=$MODEL_DIR/out_$ID # output directory for model
WORK_DIR=.

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

#fairseq-train $IN_DIR/fairseq-data-bin-$ID \
#  --pretrained-xlm-checkpoint $WORK_DIR/models/xlmr.base/model.pt --task translation_from_pretrained_xlm \
#  --encoder-learned-pos --decoder-learned-pos --max-source-positions 512 \
#  --arch transformer_xlm_iwslt_decoder --optimizer adam --lr 0.0005 -s nl -t ql \
#  --label-smoothing 0.1 --dropout 0.3 --max-tokens 4000 \
#  --lr-scheduler inverse_sqrt --weight-decay 0.0001 \
#  --criterion label_smoothed_cross_entropy --scoring bleu \
#  --warmup-updates 4000 --warmup-init-lr '1e-07' \
#  --max-epoch 200 --save-interval 30 --valid-subset valid \
#  --adam-betas '(0.9, 0.98)' --save-dir $MODEL_DIR \
#  --batch-size 256 --keep-best-checkpoints 1 --patience 20 \
#  --eval-bleu \
#  --eval-bleu-args '{"beam": 5, "max_len_a": 1.2, "max_len_b": 10}' \
#  --eval-bleu-detok space \
#  --eval-bleu-remove-bpe \
#  --best-checkpoint-metric bleu --maximize-best-checkpoint-metric \
#  --stop-time-hours 12 --cpu  \
#  --tensorboard-logdir $OUT_DIR

#langs=ar_AR,cs_CZ,de_DE,en_XX,es_XX,et_EE,fi_FI,fr_XX,gu_IN,hi_IN,it_IT,ja_XX,kk_KZ,ko_KR,lt_LT,lv_LV,my_MM,ne_NP,nl_XX,ro_RO,ru_RU,si_LK,tr_TR,vi_VN,zh_CN
#fairseq-train $IN_DIR/fairseq-data-bin-$ID \
#  --encoder-normalize-before --decoder-normalize-before \
#  --arch mbart_large --task translation_from_pretrained_bart \
#  --source-lang nl --target-lang ql \
#  --criterion label_smoothed_cross_entropy --label-smoothing 0.2  \
#  --dataset-impl mmap --optimizer adam --adam-eps 1e-06 --adam-betas '(0.9, 0.98)' \
#  --lr-scheduler polynomial_decay --lr 3e-05 \
#  --warmup-updates 2500 --max-update 40000 --dropout 0.3 --attention-dropout 0.1  \
#  --weight-decay 0.0 --max-tokens 768 --update-freq 2 --save-interval 1 \
#  --save-interval-updates 8000 --keep-interval-updates 10 \
#  --no-epoch-checkpoints --seed 222 --log-format simple --log-interval 2 \
#  --reset-optimizer --reset-meters --reset-dataloader --reset-lr-scheduler \
#  --restore-file models/mbart.cc25/model.pt --langs $langs --layernorm-embedding  \
#  --save-dir $OUT_DIR --cpu

langs=ar_AR,cs_CZ,de_DE,en_XX,es_XX,et_EE,fi_FI,fr_XX,gu_IN,hi_IN,it_IT,ja_XX,kk_KZ,ko_KR,lt_LT,lv_LV,my_MM,ne_NP,nl_XX,ro_RO,ru_RU,si_LK,tr_TR,vi_VN,zh_CN
PRETRAIN=models/mbart.cc25/model.pt

fairseq-train $IN_DIR/fairseq-data-bin-$ID \
  --encoder-normalize-before --decoder-normalize-before \
  --arch mbart_large --layernorm-embedding \
  --task translation_from_pretrained_bart \
  --source-lang en_XX --target-lang ql \
  --criterion label_smoothed_cross_entropy --label-smoothing 0.2 \
  --optimizer adam --adam-eps 1e-06 --adam-betas '(0.9, 0.98)' \
  --lr-scheduler polynomial_decay --lr 3e-05 --warmup-updates 2500 --total-num-update 40000 \
  --dropout 0.3 --attention-dropout 0.1 --weight-decay 0.0 \
  --max-tokens 1024 --update-freq 2 \
  --save-interval 1 --save-interval-updates 5000 --keep-interval-updates 10 --no-epoch-checkpoints \
  --seed 222 --log-format simple --log-interval 2 \
  --restore-file $PRETRAIN \
  --reset-optimizer --reset-meters --reset-dataloader --reset-lr-scheduler \
  --langs $langs \
  --ddp-backend legacy_ddp \
  --eval-bleu \
    --eval-bleu-args '{"beam": 5, "max_len_a": 1.2, "max_len_b": 10}' \
    --eval-bleu-detok space \
    --eval-bleu-remove-bpe \
    --best-checkpoint-metric bleu --maximize-best-checkpoint-metric \
    --cpu  \
    --tensorboard-logdir $OUT_DIR











