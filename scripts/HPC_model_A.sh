#!/usr/local_rwth/bin/zsh

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=7G
#SBATCH --time=15:00:00
#SBATCH --job-name=ALPHA
#SBATCH --output=output-%J.log

module switch intel gcc
module load python

# All names known in train set, NO TRAINING ON ALIGNMENTS

# Adapt the three variables below as required. The corresponding language files .ql and .nl, bpe.codes
# must be in 5_model_input folder.
ID=31743
ID_MODEL=ALPHA
TEST_TEMPLATES=test_templates

WORK_DIR=$HOME/nqm
SRC_DIR=$HOME/.local/bin # location of installed packages
DATA_DIR=$WORK_DIR/data/eiopa/1_external
IN_DIR=$WORK_DIR/data/eiopa/5_model_input # model input folder
FILE=$IN_DIR/data_"$ID"/data_$ID # Files used for preprocessing
MODEL_DIR=$WORK_DIR/models/$ID_MODEL
OUT_DIR=$MODEL_DIR/out_$ID # output directory for model
COUNT_TEST=$((`ls -l $FILE-test*.nl | wc -l`))
DATA_BIN=$IN_DIR/fairseq-data-bin-$ID

#pip3 install --quiet --user -r $WORK_DIR/requirements.txt
#pip3 install --quiet --user fairseq

mkdir -p $MODEL_DIR/out_$ID

[[ -d "$FILE" ]] && echo "$FILE exists"

[[ -d "$DATA_BIN" ]] \
 && { echo "$DATA_BIN already exists"} \
 || { . scripts/_build_fairseq_dataset.sh HPC $ID }

echo "Model training is started"
$SRC_DIR/fairseq-train $DATA_BIN \
  --arch transformer_iwslt_de_en --optimizer adam --lr 0.0005 -s nl -t ql \
  --label-smoothing 0.1 --dropout 0.3 --max-tokens 4000 \
  --lr-scheduler inverse_sqrt --weight-decay 0.0001 \
  --criterion label_smoothed_cross_entropy --scoring sacrebleu \
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
  --tensorboard-logdir $MODEL_DIR/out_$ID/

. scripts/_fairseq_evaluation_subwords.sh HPC No-BPE $ID $ID_MODEL