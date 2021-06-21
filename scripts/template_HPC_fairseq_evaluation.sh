#!/usr/local_rwth/bin/zsh

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=7G
#SBATCH --time=2:00:00
#SBATCH --job-name=10752
#SBATCH --output=output-%J.log

# not checked whether working

module switch intel gcc
module load python

ID=10752
ID_MODEL=$ID

WORK_DIR=$HOME/nqm
SRC_DIR=$HOME/.local/bin # location of installed packages
DATA_DIR=$WORK_DIR/data/eiopa/1_external
TEST_TEMPLATES=test_templates
IN_DIR=$WORK_DIR/data/eiopa/5_model_input # model input folder
FILE=$IN_DIR/data_$ID # Files used for preprocessing
MODEL_DIR=$WORK_DIR/models/transformer_iwslt_de_en_$ID_MODEL
OUT_DIR=$MODEL_DIR/out_$ID # output directory for model
COUNT_TEST=$((`ls -l $DATA_DIR/$TEST_TEMPLATES/*.csv | wc -l` ))


. scripts/_fairseq_evaluation_align.sh HPC BPE $ID $ID_MODEL


#
#pip3 install --quiet --user -r $WORK_DIR/requirements.txt
#pip3 install --quiet --user fairseq
#
#mkdir -p $MODEL_DIR/out_$ID
#
#[[ -d "$WORK_DIR" ]] && echo "$WORK_DIR exists"
#
#[[ -d "$IN_DIR/fairseq-data-bin-$ID" ]] \
# && { echo "fairseq-data-bin-$ID  exists" }
#
#for f in test_{1..$COUNT_TEST}; do
#  echo "Generate translations using fairseq-generate for $f"
#  $SRC_DIR/fairseq-generate $IN_DIR/fairseq-data-bin-$ID \
#    --gen-subset $f \
#    --path $MODEL_DIR/checkpoint_best.pt \
#    --results-path $OUT_DIR \
#    --beam 5  \
#    --batch-size 128 \
#    --scoring bleu \
#    --remove-bpe
#
#  echo "Decode the queries for $f"
#  python3 src/decode_fairseq_output.py \
#    --in-file $MODEL_DIR/out_$ID/generate-$f.txt \
#    --out-file $OUT_DIR/decoded-$f.txt \
#    --summary-file $OUT_DIR/summary-$ID.txt
#
#  echo "Evaluate query performance"
#  python3 src/query_results_evaluation.py \
#    --graph-path $DATA_DIR \
#    --query-file $OUT_DIR/decoded-$f.txt \
#    --out-file $OUT_DIR/queries_and_results-$f.txt \
#    --summary-file $OUT_DIR/summary-$ID.txt
#done
