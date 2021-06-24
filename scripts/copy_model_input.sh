#!/bin/zsh

# This script copies the required model files using $ID and places them in the
# correct directory. The name is adapted using $ID_new.

# Use this script from the root using the following structur:
# bash scripts/copy_model_input.sh ID ID_NEW BPE OOV XLMR
# Explanation of parameters:
#   ID: long form of ID used in data generation scripts
#   ID_new: shorter form of ID, used for model_input
#   BPE: set to YES, if some sort of subword processing was used, otherwise NO
#   OOV: set to YES, if Out-Of-Vocabulary words were replaced in the generation process
#   XLMR: set to YES, if generating data for a XLMR model

if [ -n "$1" ] && [ -n "$2" ]; then
  ID=$1
  ID_NEW=$2
  BPE=$3
  OOV=$4
  XLMR=$5
else
  ID=16-06_14-50_7633
  ID_NEW=7633
  BPE=NO
  OOV=NO
  XLMR=NO
fi

OUT_DIR=data/eiopa/3_processed
DICT_DIR=data/eiopa/4_vocabularies
INT_DIR=data/eiopa/2_interim
TGT_DIR=data/eiopa/5_model_input
COUNT_TEST=$((`ls -l $OUT_DIR/*"$ID"-test*.nl | wc -l`))


# Copy language pairs to correct folder
for L in nl ql; do
    for f in train.$L val.$L test_{1..$COUNT_TEST}.$L; do
        echo "copying ${f}..."
        cp -R $OUT_DIR/data_"$ID"-$f $TGT_DIR/data_"$ID_NEW"-$f
    done
done

# Copy helper files
if [ $XLMR = YES ]; then
  # copy XLMR input dictionary as .nl dictionary
  cp -R data/eiopa/1_external/dict.xlmr.txt $DICT_DIR/dict-$ID.nl
else :
  # copy iwslt external dictionary, is this really necessary? This is likely a mistake and
#  and overwrites the present correct dictionary
#  cp -R data/eiopa/1_external/dict.iwslt.en $DICT_DIR/dict_$ID_NEW.nl
fi
echo "copying train_$ID_NEW.align ..."
cp -R $DICT_DIR/train_$ID.align $TGT_DIR/train_$ID_NEW.align
if [ -f $DICT_DIR/bpe-$ID.codes ]
  then cp -R $DICT_DIR/bpe-$ID.codes $TGT_DIR/$ID_NEW-bpe.codes
fi
for L in nl ql; do
  if [ -f $DICT_DIR/dict-$ID.$L ]
   then cp -R $DICT_DIR/dict-$ID.$L $TGT_DIR/dict_$ID_NEW.$L
        echo "copying dict-$ID_NEW.$L..."
  fi
done
for L in nl ql; do # if BPE dicts are presented, these ones have to be used, overwrite previous copied dicts
  if [ -f $DICT_DIR/dict-$ID.bpe.$L ]
    then cp -R $DICT_DIR/dict-$ID.bpe.$L $TGT_DIR/dict_$ID_NEW.$L
         echo "copying dict-$ID_NEW.bpe.$L..."
  fi
done
if [ $BPE = YES ]; then # copy non-BPE processed files for evaluation
  for L in nl ql; do
    for f in test_{1..$COUNT_TEST}.$L; do
      cp -R $INT_DIR/data_"$ID"-$f $TGT_DIR/data_"$ID_NEW"_no-BPE-$f
      echo "copying no-BPE-$f..."
    done
  done
fi
if [ $OOV = YES ]; then
  for L in nl ql; do
    for f in val.$L test_{1..$COUNT_TEST}.$L; do
      cp -R $INT_DIR/data_"$ID"-$f $TGT_DIR/data_"$ID_NEW"_OOV-$f
      echo "Copying OOV-$f"
    done
  done
fi