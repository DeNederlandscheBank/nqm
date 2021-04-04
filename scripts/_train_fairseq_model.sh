# #!/bin/bash

DATA_DIR=../data/eiopa/4_dictionaries
MODEL_DIR=../models
ID=31181 # find in build script or end of fairseq-data-bin

mkdir -p $MODEL_DIR/checkpoints

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

fairseq-train $DATA_DIR/fairseq-data-bin-$ID \
-a transformer_iwslt_de_en --optimizer adam --lr 0.0005 -s nl -t ql \
--label-smoothing 0.1 --dropout 0.3 --max-tokens 4000 \
--min-lr '1e-09' --lr-scheduler inverse_sqrt --weight-decay 0.0001 \
--criterion label_smoothed_cross_entropy \
--warmup-updates 4000 --warmup-init-lr '1e-07' \
--max-epoch 500 --save-interval 50 --valid-subset valid,test \
--adam-betas '(0.9, 0.98)' --save-dir $MODEL_DIR/transformer_iwslt_de_en \
--batch-size 256
