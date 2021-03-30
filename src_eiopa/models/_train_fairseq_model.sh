# #!/bin/bash
#
DATA_DIR=../../data/eiopa/4_dictionaries
MODEL_DIR=../../models

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

fairseq-train \
    $DATA_DIR/fairseq-data-bin --cpu \
    --save-dir $MODEL_DIR/checkpoints/wmt16 \
    --finetune-from-model $MODEL_DIR/wmt16.en-de.joined-dict.transformer/model.pt
