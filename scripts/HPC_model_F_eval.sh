#!/usr/local_rwth/bin/zsh

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=7G
#SBATCH --time=15:00:00
#SBATCH --job-name=FOXTROTT
#SBATCH --output=output-%J.log

module switch intel gcc
module load python

# SUBWORDS, names known and unknown

# Adapt the three variables below as required. The corresponding language files .ql and .nl, bpe.codes
# must be in 5_model_input folder.
ID=21846
ID_MODEL=FOXTROTT
TEST_TEMPLATES=test_templates

WORK_DIR=$HOME/nqm
SRC_DIR=$HOME/.local/bin # location of installed packages
DATA_DIR=$WORK_DIR/data/eiopa/1_external
IN_DIR=$WORK_DIR/data/eiopa/5_model_input # model input folder
FILE=$IN_DIR/data_$ID/data_$ID # Files used for preprocessing
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


. scripts/_fairseq_evaluation_subwords.sh HPC BPE $ID $ID_MODEL