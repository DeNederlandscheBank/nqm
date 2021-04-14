#!/usr/local_rwth/bin/zsh

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=7G
#SBATCH --time=1:00:00
#SBATCH --job-name=fairseq_transformer
#SBATCH --output=output-%J.log

module switch intel gcc
module load python

WORK_DIR=$HOME/nqm
MODEL_DIR=$WORK_DIR/models
SRC_DIR=$HOME/.local/bin
IN_DIR=$WORK_DIR/data/eiopa/5_model_input
FILE=$IN_DIR/data_1689
ID=1689
OUT_FILE=$MODEL_DIR/out_$ID/translations.txt

pip3 install --quiet --user -r $WORK_DIR/requirements.txt
pip3 install --quiet --user fairseq

[[ -d "$WORK_DIR" ]] && echo "$WORK_DIR exists"

[[ -d "$IN_DIR/fairseq-data-bin-$ID" ]] \
 && { echo "fairseq-data-bin-$ID already exists"} \
 || { $SRC_DIR/fairseq-preprocess -s nl -t ql --trainpref $FILE-train \
      --validpref $FILE-val --testpref $FILE-test_1 \
      --destdir $IN_DIR/fairseq-data-bin-$ID }

echo "Model training is started"
$SRC_DIR/fairseq-train $IN_DIR/fairseq-data-bin-$ID \
 -a transformer_iwslt_de_en --optimizer adam --lr 0.0005 -s nl -t ql \
 --label-smoothing 0.1 --dropout 0.3 --max-tokens 4000 \
 --min-lr '1e-09' --lr-scheduler inverse_sqrt --weight-decay 0.0001 \
 --criterion label_smoothed_cross_entropy --scoring bleu \
 --warmup-updates 4000 --warmup-init-lr '1e-07' \
 --max-epoch 2 --save-interval 2 --valid-subset valid \
 --adam-betas '(0.9, 0.98)' --save-dir $MODEL_DIR/transformer_iwslt_de_en \
 --batch-size 256 --keep-best-checkpoints 1 --patience 50
  --eval-bleu \
  --eval-bleu-args '{"beam": 5}' \
  --eval-bleu-detok \
  --eval-bleu-remove-bpe \
  --best-checkpoint-metric bleu --maximize-best-checkpoint-metric

echo "Generate translations using fairseq-generate"
fairseq-generate $IN_DIR/fairseq-data-bin-$ID \
  --gen-subset test \
  --path $MODEL_DIR/checkpoint_best.pt \
  --results-path $MODEL_DIR/out_$ID \
  --beam 5  \
  --batch-size 128 \
  --scoring bleu \
  --remove-bpe

echo "Decode the queries"
python src_eiopa/evaluation/decode_fairseq_output.py \
  --in-file $MODEL_DIR/out_$ID/generate-test.txt \
  --out-file $OUT_FILE
