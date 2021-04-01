#!/usr/local_rwth/bin/zsh

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=8G
#SBATCH --time=0:15:00
#SBATCH --job-name=fairseq_transformer
#SBATCH --output=outputs/output-%J.log

WORK_DIR = $HOME/nqm
MODEL_DIR=$WORK_DIR/models
SRC_DIR=$HOME/.local/lib/python3.8/site-packages/fairseq_cli
IN_DIR=$WORK_DIR/data/eiopa/4_dictionaries
FILE=$IN_DIR/data_24-03_14-14_31181
ID=31181


module switch intel gcc
module load python

pip3 install --user -r $WORK_DIR/requirements.txt
pip3 install --user fairseq

if ! [ -f "$IN_DIR/fairseq-data-bin-$ID" ]; then
    python3 $SRC_DIR/preprocess.py -s nl -t ql --trainpref $FILE-train --validpref $FILE-val --testpref $FILE-test_1 --destdir $IN_DIR/fairseq-data-bin-$ID
fi

python3 $SRC_DIR/train.py $DATA_DIR/fairseq-data-bin-$ID \
-a transformer_iwslt_de_en --optimizer adam --lr 0.0005 -s nl -t ql \
--label-smoothing 0.1 --dropout 0.3 --max-tokens 4000 \
--min-lr '1e-09' --lr-scheduler inverse_sqrt --weight-decay 0.0001 \
--criterion label_smoothed_cross_entropy \
--warmup-updates 4000 --warmup-init-lr '1e-07' \
--max-epoch 1 --save-interval 50 --valid-subset valid \
--adam-betas '(0.9, 0.98)' --save-dir $MODEL_DIR/transformer_iwslt_de_en
