#!/usr/local_rwth/bin/zsh

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=8G
#SBATCH --time=12:00:00
#SBATCH --job-name=fairseq_transformer
#SBATCH --output=output-%J.log

module switch intel gcc
module load python

# NO SUBWORDS, NO TRAINING ON ALIGNMENTS, EXTERNAL NL DICT

# Adapt the three variables below as required. The corresponding language files .ql and .nl, bpe.codes
# must be in 5_model_input folder.
ID=5861
ID_MODEL=$ID
TEST_TEMPLATES=test_templates

WORK_DIR=$HOME/nqm
SRC_DIR=$HOME/.local/bin # location of installed packages
DATA_DIR=$WORK_DIR/data/eiopa/1_external
IN_DIR=$WORK_DIR/data/eiopa/5_model_input # model input folder
FILE=$IN_DIR/data_$ID # Files used for preprocessing
MODEL_DIR=$WORK_DIR/models/transformer_iwslt_de_en_$ID_MODEL
OUT_DIR=$MODEL_DIR/out_$ID # output directory for model
COUNT_TEST=$((`ls -l $DATA_DIR/$TEST_TEMPLATES/*.csv | wc -l` ))
DATA_BIN=$IN_DIR/fairseq-data-bin-$ID

pip3 install --quiet --user -r $WORK_DIR/requirements.txt
pip3 install --quiet --user fairseq

mkdir -p $MODEL_DIR/out_$ID

[[ -d "$FILE" ]] && echo "$FILE exists"

[[ -d "$IN_DIR/fairseq-data-bin-$ID" ]] \
 && { echo "fairseq-data-bin-$ID already exists"} \
 || { $SRC_DIR/fairseq-preprocess -s nl -t ql --trainpref $FILE-train \
      --validpref $FILE-val \
      --destdir $DATA_BIN \
      --srcdict $DATA_DIR/dict.iwslt.en \
      --tgtdict $IN_DIR/dict_$ID.ql \
      --alignfile $IN_DIR/train_$ID.align

      for f in test_{1..$COUNT_TEST}; do
        # Create multiple files using dictionary from above
        # this goes into different folders due to fairseq
        $SRC_DIR/fairseq-preprocess -s nl -t ql \
          --testpref $FILE-$f \
          --destdir $DATA_BIN-$f \
          --cpu --empty-cache-freq 10 \
          --srcdict $DATA_DIR/dict.iwslt.en \
          --tgtdict $IN_DIR/dict_$ID.ql
        # collect all test files in one folder and rename them
        for L in nl ql; do
          for S in bin idx; do
            echo "Copying $f.nl-ql.$L.$S"
            cp -R $DATA_BIN-$f/test.nl-ql.$L.$S \
             $DATA_BIN/$f.nl-ql.$L.$S
          done
        done
        echo "Deleting folder $DATA_BIN-$f/"
        rm -R $DATA_BIN-$f/
      done
    }

echo "Model training is started"
$SRC_DIR/fairseq-train $IN_DIR/fairseq-data-bin-$ID \
  --arch transformer_align --optimizer adam --lr 0.0005 -s nl -t ql \
  --label-smoothing 0.1 --dropout 0.3 --max-tokens 4000 \
  --min-lr '1e-09' --lr-scheduler inverse_sqrt --weight-decay 0.0001 \
  --criterion label_smoothed_cross_entropy_with_alignment --scoring bleu \
  --warmup-updates 4000 --warmup-init-lr '1e-07' \
  --max-epoch 200 --save-interval 30 --valid-subset valid \
  --adam-betas '(0.9, 0.98)' --save-dir $MODEL_DIR \
  --batch-size 256 --keep-best-checkpoints 1 --patience 20 \
  --eval-bleu \
  --eval-bleu-args '{"beam": 5, "max_len_a": 1.2, "max_len_b": 10}' \
  --eval-bleu-detok space \
  --eval-bleu-remove-bpe \
  --best-checkpoint-metric bleu --maximize-best-checkpoint-metric \
  --stop-time-hours 11 --cpu  \
  --tensorboard-logdir $MODEL_DIR/out_$ID/ \

for f in test_{1..$COUNT_TEST}; do
  echo "Generate translations using fairseq-generate for $f"
  $SRC_DIR/fairseq-generate $IN_DIR/fairseq-data-bin-$ID \
    --gen-subset $f \
    --path $MODEL_DIR/checkpoint_best.pt \
    --results-path $OUT_DIR \
    --beam 5  \
    --batch-size 128 \
    --scoring bleu \
    --remove-bpe --replace-unk --print-alignment

  echo "Decode the queries for $f"
  python3 src_eiopa/decode_fairseq_output.py \
    --in-file $MODEL_DIR/out_$ID/generate-$f.txt \
    --out-file $OUT_DIR/decoded-$f.txt \
    --summary-file $OUT_DIR/summary-$ID.txt

  echo "Evaluate query performance"
  python3 src_eiopa/query_results_evaluation.py \
    --graph-path $DATA_DIR \
    --query-file $OUT_DIR/decoded-$f.txt \
    --out-file $OUT_DIR/queries_and_results-$f.txt \
    --summary-file $OUT_DIR/summary-$ID.txt
done