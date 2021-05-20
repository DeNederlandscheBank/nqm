#!/usr/local_rwth/bin/zsh

# INSTRUCTIONS:
# When using this script, two arguments have to be given:
# 1 whether the script is to be used locally or on the HPC Aachen (argument: HPC)
# As argument 2 and 3, the data ID and model_ID can be given, but not required
# Example: "source _fairseq_evaluation_align.sh HPC BPE 5861 5861"

# This script will conduct replacement of OOV words in the target hypothesis and requires
# an alignment dictionary (automatically generated when using data_eiopa_alignments.sh)

ID=883
ID_MODEL=$ID

if [ $1 = HPC ]
    then  WORK_DIR=$HOME/nqm
          SRC_DIR=$HOME/.local/bin # location of installed packages
          generate=$SRC_DIR/fairseq-interactive
          PYTHON=python3
else
    WORK_DIR=.
    generate=fairseq-interactive
    PYTHON=python3
fi
if [ -n "$2" ]
    then ID=$2
else
  DATA_DIR=$WORK_DIR/data/eiopa/1_external
  TEST_TEMPLATES=test_templates
  IN_DIR=$WORK_DIR/data/eiopa/5_model_input # model input folder
  FILE=$IN_DIR/data_$ID # Files used for preprocessing
  MODEL_DIR=$WORK_DIR/models/transformer_pointer_generator_iwslt_de_en_$ID_MODEL
  OUT_DIR=$MODEL_DIR/out_$ID # output directory for model
  COUNT_TEST=$((`ls -l $DATA_DIR/$TEST_TEMPLATES/*.csv | wc -l` ))
  DATA_BIN=$IN_DIR/fairseq-data-bin-$ID
fi
if [ -n "$3" ]
    then ID_MODEL=$3
fi
CHECKPOINT_BEST_BLEU=$(find $MODEL_DIR -name 'checkpoint.best_bleu_*.pt')
BPE_CODES=$IN_DIR/$ID-bpe.codes
ALIGN_FILE=$DATA_BIN/alignment.nl-ql.txt
DATA_BIN=$IN_DIR/fairseq-data-bin-$ID

mkdir -p $OUT_DIR

[[ -d "$DATA_BIN" ]] \
 && { echo "$DATA_BIN  exists" }

for f in test_{1..$COUNT_TEST}; do
  echo "Generate translations using fairseq-interactive for $f"
  cat $IN_DIR/data_$ID-$f.nl | \
        $generate $DATA_BIN \
          --path $CHECKPOINT_BEST_BLEU \
          --results-path $OUT_DIR --beam 5  \
          --print-alignment \
          --skip-invalid-size-inputs-valid-test \
        > $OUT_DIR/generate-$f.txt

  echo "Decode the queries for $f and evaluate the translation"
  $PYTHON src_eiopa/decode_fairseq_output.py \
    --interactive --pointer-generator \
    --in-file $MODEL_DIR/out_$ID/generate-$f.txt \
    --out-file $OUT_DIR/decoded-$f.txt \
    --out-file-encoded $OUT_DIR/translations-$f.txt \
    --in-file-reference $IN_DIR/data_"$ID"_OOV-$f.ql \
    --summary-file $OUT_DIR/summary-$ID.txt \
    --graph-path data/eiopa/1_external \
    --in-file-source $IN_DIR/data_"$ID"_OOV-$f.nl

  echo "Evaluate query performance"
  $PYTHON src_eiopa/query_results_evaluation.py \
    --interactive \
    --graph-path $DATA_DIR \
    --query-file $OUT_DIR/decoded-$f.txt \
    --out-file $OUT_DIR/queries_and_results-$f.txt \
    --summary-file $OUT_DIR/summary-$ID.txt
done
