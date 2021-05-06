#!/usr/local_rwth/bin/zsh

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=7G
#SBATCH --time=4:00:00
#SBATCH --job-name=10752-align
#SBATCH --output=output-%J.log

# not checked whether working

module switch intel gcc
module load python

ID=10752
ID_MODEL=$ID-align
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


. scripts/_fairseq_evaluation_align.sh HPC BPE $ID $ID_MODEL
