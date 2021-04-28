
DATABIN=data/eiopa/2_interim/fairseq-dev
OUT_DIR=5

#sh scripts/generate_dict.sh

if [ -d $DATABIN ]; then
  rm -r $DATABIN
fi

fairseq-preprocess -s nl -t ql \
  --trainpref data/eiopa/2_interim/data_27-04_15-02_10578-dev-val.bpe \
  --validpref data/eiopa/2_interim/data_27-04_15-02_10578-dev-val.bpe \
  --destdir $DATABIN \
  --cpu --empty-cache-freq 10 \
  --srcdict data/eiopa/1_external/dict.iwslt.en \
  --tgtdict data/eiopa/2_interim/10578-dev-train_val.ql.dict
#  --alignfile data/eiopa/2_interim/10578-dev-train.align \
#  --dataset-impl raw

echo $OUT_DIR