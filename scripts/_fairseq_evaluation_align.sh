#!/usr/local_rwth/bin/zsh

# INSTRUCTIONS:
# When using this script, two arguments have to be given:
# -1 whether the script is to be used locally or on the HPC Aachen (argument: HPC)
# -2 whether subword processing was used for training the model (argument: BPE)
# As argument 3 and 4, the data ID and model_ID can be given, but not required
# Example: "source _fairseq_evaluation_align.sh HPC BPE 5861 5861"

# This script will conduct replacement of OOV words in the target hypothesis and requires
# an alignment dictionary (automatically generated when using data_eiopa_alignments.sh)

ID=5861
ID_MODEL=$ID

if [ $1 = HPC ]
    then  WORK_DIR=$HOME/nqm
          SRC_DIR=$HOME/.local/bin # location of installed packages
          generate=$SRC_DIR/fairseq-interactive
          PYTHON=python3
          pip3 install --quiet --user -r $WORK_DIR/requirements.txt
else
    WORK_DIR=.
    generate=fairseq-interactive
    PYTHON=python3
fi
if [ $2 = BPE ]
    then SUBWORDS=True
else
  SUBWORDS=False
fi
if [ -n "$3" ]
    then ID=$3
else
  DATA_DIR=$WORK_DIR/data/eiopa/1_external
  TEST_TEMPLATES=test_templates
  IN_DIR=$WORK_DIR/data/eiopa/5_model_input # model input folder
  FILE=$IN_DIR/data_$ID # Files used for preprocessing
  MODEL_DIR=$WORK_DIR/models/transformer_iwslt_de_en_$ID_MODEL
  OUT_DIR=$MODEL_DIR/out_$ID # output directory for model
  COUNT_TEST=$((`ls -l $DATA_DIR/$TEST_TEMPLATES/*.csv | wc -l` ))
fi
if [ -n "$4" ]
    then ID_MODEL=$4
fi
CHECKPOINT_BEST_BLEU=$(find $MODEL_DIR -name 'checkpoint.best_bleu_*.pt')
BPE_CODES=$IN_DIR/$ID-bpe.codes
ALIGN_FILE=$IN_DIR/fairseq-data-bin-$ID/alignment.nl-ql.txt

mkdir -p $MODEL_DIR/out_$ID

[[ -d "$IN_DIR/fairseq-data-bin-$ID" ]] \
 && { echo "fairseq-data-bin-$ID  exists" }

for f in test_{1..$COUNT_TEST}; do
  echo "Generate translations using fairseq-interactive for $f"
  if [ $SUBWORDS = True ]
    then  cat $IN_DIR/data_$ID-$f.nl | \
          $generate $IN_DIR/fairseq-data-bin-$ID \
            --path $CHECKPOINT_BEST_BLEU \
            --results-path $OUT_DIR --beam 5  \
            --print-alignment --replace-unk $ALIGN_FILE \
            --bpe subword_nmt --bpe-codes $BPE_CODES \
          > $MODEL_DIR/out_$ID/generate-$f.txt
  else
    cat $IN_DIR/data_$ID-$f.nl | \
          $generate $IN_DIR/fairseq-data-bin-$ID \
            --path $CHECKPOINT_BEST_BLEU \
            --results-path $OUT_DIR --beam 5  \
            --print-alignment --replace-unk $ALIGN_FILE \
          > $MODEL_DIR/out_$ID/generate-$f.txt
  fi

  echo "Decode the queries for $f and evaluate the translation"
  $PYTHON src_eiopa/decode_fairseq_output.py \
     --interactive \
     --in-file $MODEL_DIR/out_$ID/generate-$f.txt \
     --out-file $OUT_DIR/decoded-$f.txt \
     --out-file-encoded $OUT_DIR/translations-$f.txt \
     --in-file-reference $IN_DIR/data_$ID-$f.ql \
     --summary-file $OUT_DIR/summary-$ID.txt \
     --graph-path data/eiopa/1_external

  echo "Evaluate query performance"
  $PYTHON src_eiopa/query_results_evaluation.py \
    --interactive \
    --graph-path $DATA_DIR \
    --query-file $OUT_DIR/decoded-$f.txt \
    --out-file $OUT_DIR/queries_and_results-$f.txt \
    --summary-file $OUT_DIR/summary-$ID.txt
done