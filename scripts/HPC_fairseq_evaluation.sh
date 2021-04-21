#!/usr/local_rwth/bin/zsh

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=8G
#SBATCH --time=1:00:00
#SBATCH --job-name=fairseq_evaluation
#SBATCH --output=output-%J.log

module switch intel gcc
module load python

ID=14126
TEST_TEMPLATES=test_templates
WORK_DIR=$HOME/nqm
SRC_DIR=$HOME/.local/bin
IN_DIR=$WORK_DIR/data/eiopa/5_model_input
FILE=$IN_DIR/data_$ID
MODEL_DIR=$WORK_DIR/models/transformer_iwslt_de_en_$ID
OUT_FILE=$MODEL_DIR/out_$ID/translations.txt
DATA_DIR=$WORK_DIR/data/eiopa/1_external
OUT_DIR=$MODEL_DIR/out_$ID
COUNT_TEST=$((`ls -l $DATA_DIR/$TEST_TEMPLATES/*.csv | wc -l` ))
DATA_BIN=$OUT_DIR/fairseq-data-bin-$ID

pip3 install --quiet --user -r $WORK_DIR/requirements.txt
pip3 install --quiet --user fairseq

mkdir -p $MODEL_DIR/out_$ID

[[ -d "$WORK_DIR" ]] && echo "$WORK_DIR exists"

[[ -d "$IN_DIR/fairseq-data-bin-$ID" ]] \
 && { echo "fairseq-data-bin-$ID already exists"} \
 || { $SRC_DIR/fairseq-preprocess -s nl -t ql --trainpref $FILE-train \
      --validpref $FILE-val \
      --destdir $IN_DIR/fairseq-data-bin-$ID }

for f in test_{1..$COUNT_TEST}; do
  # Create multiple files using dictionary from above
  # this goes into different folders due to fairseq
  fairseq-preprocess -s nl -t ql \
    --testpref $FILE-$f \
    --destdir $DATA_BIN-$f \
    --cpu --empty-cache-freq 10 \
    --srcdict $DATA_BIN/dict.nl.txt \
    --tgtdict $DATA_BIN/dict.ql.txt
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

for f in test_{1..$COUNT_TEST}; do
  echo "Generate translations using fairseq-generate for $f"
  fairseq-generate $IN_DIR/fairseq-data-bin-$ID \
    --gen-subset $f \
    --path $MODEL_DIR/checkpoint_best.pt \
    --results-path $OUT_DIR \
    --beam 5  \
    --batch-size 128 \
    --scoring bleu \
    --remove-bpe

  mv $OUT_DIR/generate-test.txt $OUT_DIR/generate-$f.txt

  echo "Decode the queries for $f"
  python src_eiopa/decode_fairseq_output.py \
    --in-file $MODEL_DIR/out_$ID/generate-$f.txt \
    --out-file $OUT_DIR/encoded-$f.txt \
    --summary-file $OUT_DIR/summary-$ID.txt
done