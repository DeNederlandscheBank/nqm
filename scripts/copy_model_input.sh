#!/bin/zsh

# Use this script from the root!
# This script copies the required model files using $ID and places them in the
# correct directory. The name is adapated using $ID_new. These two variables
# have to be adapted to the desired values.
ID=19-05_19-03_15285
ID_NEW=15285
BPE=NO


DATA_DIR=data/eiopa/3_processed
VOC_DIR=data/eiopa/4_vocabularies
INT_DIR=data/eiopa/2_interim
TGT_DIR=data/eiopa/5_model_input
COUNT_TEST=$((`ls -l data/eiopa/1_external/test_templates/*.csv | wc -l`))


# Copy language pairs to correct folder
for L in nl ql; do
    for f in train.$L val.$L test_{1..$COUNT_TEST}.$L; do
        echo "copying ${f}..."
        cp -R $DATA_DIR/data_"$ID"-$f $TGT_DIR/data_"$ID_NEW"-$f
    done
done

# Copy helper files
cp -R data/eiopa/1_external/dict.iwslt.en $VOC_DIR/dict_$ID_NEW.nl
echo "copying train_$ID_NEW.align ..."
cp -R $VOC_DIR/train_$ID.align $TGT_DIR/train_$ID_NEW.align
if [ -f $VOC_DIR/bpe-$ID.codes ]
  then cp -R $VOC_DIR/bpe-$ID.codes $TGT_DIR/$ID_NEW-bpe.codes
fi
for L in nl ql; do
  if [ -f $VOC_DIR/dict-$ID.$L ]
   then cp -R $VOC_DIR/dict-$ID.$L $TGT_DIR/dict_$ID_NEW.$L
        echo "copying dict-$ID_NEW.$L..."
  fi
done
for L in nl ql; do # if BPE dicts are presented, these ones have to be used, overwrite previous copied dicts
  if [ -f $VOC_DIR/dict-$ID.bpe.$L ]
    then cp -R $VOC_DIR/dict-$ID.bpe.$L $TGT_DIR/dict_$ID_NEW.$L
         echo "copying dict-$ID_NEW.bpe.$L..."
  fi
done
if [ $BPE = YES ]
    then
      for L in nl ql; do
        for f in test_{1..$COUNT_TEST}.$L; do
          cp -R $INT_DIR/data_"$ID"-$f $TGT_DIR/data_"$ID_NEW"_no-BPE-$f
          echo "copying no-BPE-$f..."
        done
      done
fi
for f in test_{1..$COUNT_TEST}.nl; do
  cp -R $INT_DIR/data_"$ID"-$f $TGT_DIR/data_"$ID_NEW"_OOV-$f
  echo "Copying OOV-$f"
done