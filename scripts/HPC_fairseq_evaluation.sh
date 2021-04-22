#!/usr/local_rwth/bin/zsh

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=8G
#SBATCH --time=1:30:00
#SBATCH --job-name=fairseq_evaluation
#SBATCH --output=output-%J.log

module switch intel gcc
module load python

ID=5847
ID_MODEL=14126

WORK_DIR=$HOME/nqm
SRC_DIR=$HOME/.local/bin # location of installed packages
DATA_DIR=$WORK_DIR/data/eiopa/1_external
TEST_TEMPLATES=test_templates
IN_DIR=$WORK_DIR/data/eiopa/5_model_input # model input folder
FILE=$IN_DIR/data_$ID # Files used for preprocessing
MODEL_DIR=$WORK_DIR/models/transformer_iwslt_de_en_$ID_MODEL
OUT_DIR=$MODEL_DIR/out_$ID # output directory for model
COUNT_TEST=$((`ls -l $DATA_DIR/$TEST_TEMPLATES/*.csv | wc -l` ))

pip3 install --quiet --user -r $WORK_DIR/requirements.txt
pip3 install --quiet --user fairseq

mkdir -p $MODEL_DIR/out_$ID

[[ -d "$WORK_DIR" ]] && echo "$WORK_DIR exists"

[[ -d "$IN_DIR/fairseq-data-bin-$ID" ]] \
 && { echo "fairseq-data-bin-$ID  exists" }

for f in test_{1..$COUNT_TEST}; do
  echo "Generate translations using fairseq-generate for $f"
  $SRC_DIR/fairseq-generate $IN_DIR/fairseq-data-bin-$ID \
    --gen-subset $f \
    --path $MODEL_DIR/checkpoint_best.pt \
    --results-path $OUT_DIR \
    --beam 5  \
    --batch-size 128 \
    --scoring bleu \
    --remove-bpe

  mv $OUT_DIR/generate-test.txt $OUT_DIR/generate-$f.txt

  echo "Decode the queries for $f"
  python3 src_eiopa/decode_fairseq_output.py \
    --in-file $MODEL_DIR/out_$ID/generate-$f.txt \
    --out-file $OUT_DIR/encoded-$f.txt \
    --summary-file $OUT_DIR/summary-$ID.txt
done
