#!/usr/local_rwth/bin/zsh

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=7G
#SBATCH --time=7:00:00
#SBATCH --job-name=fairseq_transformer
#SBATCH --output=output-%J.log

module switch intel gcc
module load python

WORK_DIR=$HOME/nqm
MODEL_DIR=$WORK_DIR/models
SRC_DIR=$HOME/.local/bin
IN_DIR=$WORK_DIR/data/eiopa/4_dictionaries
FILE=$IN_DIR/data_24-03_14-14_31181
ID=31181

pip3 install --quiet --user -r $WORK_DIR/requirements.txt
pip3 install --quiet --user fairseq

[[ -d "$WORK_DIR" ]] && echo "$WORK_DIR exists"

[[ -d "$IN_DIR/fairseq-data-bin-$ID" ]] \
 && {echo "fairseq-data-bin-$ID already exists"} \
 || { $SRC_DIR/fairseq-preprocess -s nl -t ql --trainpref $FILE-train \
      --validpref $FILE-val --testpref $FILE-test_1 \
      --destdir $IN_DIR/fairseq-data-bin-$ID }

$SRC_DIR/fairseq-train $IN_DIR/fairseq-data-bin-$ID \
 -a transformer_iwslt_de_en --optimizer adam --lr 0.0005 -s nl -t ql \
 --label-smoothing 0.1 --dropout 0.3 --max-tokens 4000 \
 --min-lr '1e-09' --lr-scheduler inverse_sqrt --weight-decay 0.0001 \
 --criterion label_smoothed_cross_entropy --scoring bleu \
 --warmup-updates 4000 --warmup-init-lr '1e-07' \
 --max-epoch 300 --save-interval 50 --valid-subset valid \
 --adam-betas '(0.9, 0.98)' --save-dir $MODEL_DIR/transformer_iwslt_de_en \
 --batch-size 256 --keep-best-checkpoints 1 --patience 20
