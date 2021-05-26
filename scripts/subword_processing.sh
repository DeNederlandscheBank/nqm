#!/bin/zsh

# SPARQL and natural language dictionary has to be given as external argument

if [ -n "$3" ]
    then ID=$3
else
  ID=10578
  DATA_DIR=data/eiopa/1_external # input data location
  OUT_DIR=data/eiopa/3_processed
  INT_DIR=data/eiopa/2_interim
  DICT_DIR=data/eiopa/4_vocabularies
  COUNT_TEST=$((`ls -l $DATA_DIR/$TEST_TEMPLATES/*.csv | wc -l` ))
fi

BPE_CODE=$DICT_DIR/bpe-$ID.codes

# Merge nl and ql dictionary to learn joint subwords
cat $1 $2 > $DICT_DIR/dict-$ID.shared

echo 'Learning BPE codes using subword_nmt'
python src_eiopa/subword-nmt/subword_nmt/learn_bpe.py \
  --input $DICT_DIR/dict-$ID.shared \
  --output $BPE_CODE \
  --dict-input

# Apply bpe to all relevant files
for L in nl ql; do # both languages
    for f in train.$L val.$L test_{1..$COUNT_TEST}.$L; do
        echo "apply_bpe.py to ${f}..."
        python src_eiopa/subword-nmt/subword_nmt/apply_bpe.py \
        --codes "$BPE_CODE" \
        --input $INT_DIR/data_"$ID"-$f \
        --output $OUT_DIR/data_"$ID"-$f
    done
done

echo 'Generate new dictionaries using train...'
  for L in nl ql; do
    python src_eiopa/subword-nmt/subword_nmt/get_vocab.py \
      --input $OUT_DIR/data_$ID-train.$L --output $DICT_DIR/dict-$ID.bpe.$L
  done



#for L in nl ql; do
#  python src_eiopa/subword-nmt/subword_nmt/apply_bpe.py \
#    --input data/eiopa/2_interim/data_27-04_15-02_10578-dev-val.$L \
#    --output data/eiopa/2_interim/data_27-04_15-02_10578-dev-val.bpe.$L \
#    --codes data/eiopa/2_interim/dev-bpe.codes
#done

#echo 'Learning BPE codes using subword_nmt'
#python src_eiopa/subword-nmt/subword_nmt/learn_joint_bpe_and_vocab.py \
#  --input $INT_DIR/data_"$ID"-train.nl $INT_DIR/data_"$ID"-train.ql \
#  --output $BPE_CODE \
#  --write-vocabulary $DICT_DIR/$ID-vocab.nl $DICT_DIR/$ID-vocab.ql \
#  --symbols 100
#

#
## Apply bpe to all relevant files
#for L in nl ql; do # both languages
#    for f in train.$L val.$L test_{1..$COUNT_TEST}.$L; do
#        echo "apply_bpe.py to ${f}..."
#        python src_eiopa/subword-nmt/subword_nmt/apply_bpe.py \
#        --codes "$BPE_CODE" \
#        --input $INT_DIR/data_"$ID"-$f \
#        --output $OUT_DIR/data_"$ID"-$f \
#        --vocabulary $DICT_DIR/$ID-vocab.$L
#    done
#done
