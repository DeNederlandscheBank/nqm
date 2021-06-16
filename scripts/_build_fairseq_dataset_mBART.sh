#!/usr/local_rwth/bin/zsh
# Use this script from the root!
# Similiar to before, the ID variable needs to be corrected to the correct value.

ID=7633


if [ $1 = HPC ]
    then  WORK_DIR=$HOME/nqm
          SRC_DIR=$HOME/.local/bin # location of installed packages
          preprocess=$SRC_DIR/fairseq-preprocess
else
    WORK_DIR=.
    preprocess=fairseq-preprocess
fi
if [ -n "$2" ]; then
  ID=$2
else
  DATA_DIR=$WORK_DIR/data/eiopa/1_external
  TEST_TEMPLATES=test_templates
  IN_DIR=$WORK_DIR/data/eiopa/5_model_input # model input folder
  FILE=$IN_DIR/data_$ID # Files used for preprocessing
  MODEL_DIR=$WORK_DIR/models/transformer_iwslt_de_en_$ID_MODEL
  OUT_DIR=$MODEL_DIR/out_$ID # output directory for model
  COUNT_TEST=$((`ls -l $DATA_DIR/$TEST_TEMPLATES/*.csv | wc -l` ))
  DATA_BIN=$IN_DIR/fairseq-data-bin-$ID
fi

$preprocess -s en_XX -t ql \
      --trainpref $FILE-train \
      --validpref $FILE-val \
      --destdir $DATA_BIN \
      --srcdict $IN_DIR/dict_$ID.en_XX \
      --tgtdict $IN_DIR/dict_$ID.ql \
      --alignfile $IN_DIR/train_$ID.align \
      --cpu --empty-cache-freq 10

for f in test_{1..$COUNT_TEST}; do
  # Create multiple files using dictionary from above
  # this goes into different folders due to fairseq
  $preprocess -s en_XX -t ql \
    --testpref $FILE-$f \
    --destdir $DATA_BIN-$f \
    --cpu --empty-cache-freq 10 \
    --srcdict $IN_DIR/dict_$ID.en_XX \
    --tgtdict $IN_DIR/dict_$ID.ql \
  # collect all test files in one folder and rename them
  for L in en_XX ql; do
    for S in bin idx; do
      echo "Copying $f.en_XX-ql.$L.$S"
      cp -R $DATA_BIN-$f/test.en_XX-ql.$L.$S \
       $DATA_BIN/$f.en_XX-ql.$L.$S
    done
  done
  echo "Deleting folder $DATA_BIN-$f/"
  rm -R $DATA_BIN-$f/
done

