#!/usr/local_rwth/bin/zsh

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
if [ -n "$2" ]
    then ID=$1
else
  DATA_DIR=$WORK_DIR/data/eiopa/1_external
  TEST_TEMPLATES=test_templates
  IN_DIR=$WORK_DIR/data/eiopa/5_model_input # model input folder
  FILE=$IN_DIR/data_$ID # Files used for preprocessing
  MODEL_DIR=$WORK_DIR/models/transformer_iwslt_de_en_$ID_MODEL
  OUT_DIR=$MODEL_DIR/out_$ID # output directory for model
  COUNT_TEST=$((`ls -l $DATA_DIR/$TEST_TEMPLATES/*.csv | wc -l` ))
fi
if [ -n "$3" ]
    then ID_MODEL=$2
fi
CHECKPOINT_BEST_BLEU=$(find $MODEL_DIR -name 'checkpoint.best_bleu_*.pt')
BPE_CODES=$IN_DIR/$ID-bpe.codes
ALIGN_FILE=$IN_DIR/fairseq-data-bin-$ID/alignment.nl-ql.txt

mkdir -p $MODEL_DIR/out_$ID

[[ -d "$IN_DIR/fairseq-data-bin-$ID" ]] \
 && { echo "fairseq-data-bin-$ID  exists" }
#..$COUNT_TEST}; do
for f in test_1_dev; do
  echo "Generate translations using fairseq-interactive for $f"
  cat $IN_DIR/data_$ID-$f.nl | \
  $generate $IN_DIR/fairseq-data-bin-$ID \
    --path $CHECKPOINT_BEST_BLEU \
    --results-path $OUT_DIR --beam 5  \
    --print-alignment --replace-unk $ALIGN_FILE \
      > $MODEL_DIR/out_$ID/generate-$f.txt
     # --bpe subword_nmt --bpe-codes $BPE_CODES \


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
