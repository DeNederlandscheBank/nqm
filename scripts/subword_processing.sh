

echo 'Learning BPE codes using subword_nmt'
#python src_eiopa/subword-nmt/subword_nmt/learn_joint_bpe_and_vocab.py \
#  --input $INT_DIR/data_"$ID"-train.nl $INT_DIR/data_"$ID"-train.ql \
#  --output $BPE_CODE \
#  --write-vocabulary $DICT_DIR/$ID-vocab.nl $DICT_DIR/$ID-vocab.ql \
#  --symbols 100

#python src_eiopa/subword-nmt/subword_nmt/learn_bpe.py \
#  --input data/eiopa/2_interim/dict.dev.shared \
#  --output data/eiopa/2_interim/dev-bpe.codes \
#  --dict-input

for L in nl ql; do
  python src_eiopa/subword-nmt/subword_nmt/apply_bpe.py \
    --input data/eiopa/2_interim/data_27-04_15-02_10578-dev-val.$L \
    --output data/eiopa/2_interim/data_27-04_15-02_10578-dev-val.bpe.$L \
    --codes data/eiopa/2_interim/dev-bpe.codes
done