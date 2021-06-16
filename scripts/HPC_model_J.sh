#!/usr/local_rwth/bin/zsh

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=16G
#SBATCH --time=70:00:00
#SBATCH --job-name=JULIETT
#SBATCH --output=output-%J.log

module switch intel gcc
module load python

# mBART, same sentencepiece model for nl and ql

# Adapt the three variables below as required. The corresponding language files .ql and .nl, bpe.codes
# must be in 5_model_input folder.
ID=7633
ID_MODEL=JULIETT
TEST_TEMPLATES=test_templates

langs=ar_AR,cs_CZ,de_DE,en_XX,es_XX,et_EE,fi_FI,fr_XX,gu_IN,hi_IN,it_IT,ja_XX,kk_KZ,ko_KR,lt_LT,lv_LV,my_MM,ne_NP,nl_XX,ro_RO,ru_RU,si_LK,tr_TR,vi_VN,zh_CN
PRETRAIN=models/mbart.cc25/model.pt

WORK_DIR=$HOME/nqm
SRC_DIR=$HOME/.local/bin # location of installed packages
DATA_DIR=$WORK_DIR/data/eiopa/1_external
IN_DIR=$WORK_DIR/data/eiopa/5_model_input # model input folder
FILE=$IN_DIR/data_$ID # Files used for preprocessing
MODEL_DIR=$WORK_DIR/models/$ID_MODEL
OUT_DIR=$MODEL_DIR/out_$ID # output directory for model
COUNT_TEST=$((`ls -l $DATA_DIR/$TEST_TEMPLATES/*.csv | wc -l` ))
DATA_BIN=$IN_DIR/fairseq-data-bin-$ID

#pip3 install --quiet --user -r $WORK_DIR/requirements.txt
#pip3 install --quiet --user fairseq

mkdir -p $MODEL_DIR/out_$ID

[[ -d "$FILE" ]] && echo "$FILE exists"

[[ -d "$DATA_BIN" ]] \
 && { echo "$DATA_BIN already exists"} \
 || { . scripts/_build_fairseq_dataset_mBART.sh HPC $ID }

echo "Model training is started"
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

#. scripts/_fairseq_evaluation_align.sh HPC BPE $ID $ID_MODEL