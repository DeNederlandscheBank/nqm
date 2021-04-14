# #!/bin/bash

IN_DIR=data/eiopa/5_model_input
MODEL_DIR=models
ID=1689 # find in build script or end of fairseq-data-bin

#mkdir -p $MODEL_DIR/checkpoints

# CUDA_VISIBLE_DEVICES=0 fairseq-train \
#     $DATA_DIR/fairseq-data-bin --cpu \
#     --arch transformer --save-dir $MODEL_DIR/checkpoints/transformer \
#     --lr 0.25 --clip-norm 0.1 --dropout 0.2 --max-tokens 4000 \
#     --optimizer adam \

# mkdir -p ../features/example/checkpoints/fconv
# CUDA_VISIBLE_DEVICES=0 fairseq-train ../features/example/iwslt14.tokenized.de-en \
#     --lr 0.25 --clip-norm 0.1 --dropout 0.2 --max-tokens 4000 \
#     --arch fconv_iwslt_de_en --save-dir checkpoints/fconv \
#     --source-lang de --target-lang en

#fairseq-train $DATA_DIR/fairseq-data-bin-$ID \
#-a transformer_iwslt_de_en --optimizer adam --lr 0.0005 -s nl -t ql \
#--label-smoothing 0.1 --dropout 0.3 --max-tokens 4000 \
#--min-lr '1e-09' --lr-scheduler inverse_sqrt --weight-decay 0.0001 \
#--criterion label_smoothed_cross_entropy \
#--warmup-updates 4000 --warmup-init-lr '1e-07' \
#--max-epoch 500 --save-interval 50 --valid-subset valid,test \
#--adam-betas '(0.9, 0.98)' --save-dir $MODEL_DIR/transformer_iwslt_de_en \
#--batch-size 128

fairseq-train $IN_DIR/fairseq-data-bin-$ID \
 -a transformer_iwslt_de_en --optimizer adam --lr 0.0005 -s nl -t ql \
 --label-smoothing 0.1 --dropout 0.3 --max-tokens 4000 \
 --min-lr '1e-09' --lr-scheduler inverse_sqrt --weight-decay 0.0001 \
 --criterion label_smoothed_cross_entropy --scoring bleu \
 --warmup-updates 4000 --warmup-init-lr '1e-07' \
 --max-epoch 1 --save-interval 1 --valid-subset valid \
 --adam-betas '(0.9, 0.98)' --save-dir $MODEL_DIR/transformer_iwslt_de_en \
 --batch-size 128 --keep-best-checkpoints 1 --patience 50 \
 --eval-bleu \
  --eval-bleu-args '{"beam": 5, "max_len_a": 1.2, "max_len_b": 10}' \
  --eval-bleu-detok moses \
  --eval-bleu-remove-bpe \
  --best-checkpoint-metric bleu --maximize-best-checkpoint-metric
