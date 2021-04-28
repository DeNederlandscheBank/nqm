
DATABIN=data/eiopa/2_interim/fairseq-dev

if [ -d $DATABIN ]; then
  rm -r $DATABIN
fi

fairseq-preprocess -s nl -t ql \
  --trainpref data/eiopa/2_interim/data_27-04_15-02_10578-dev-train \
  --validpref data/eiopa/2_interim/data_27-04_15-02_10578-dev-val \
  --destdir $DATABIN \
  --cpu --empty-cache-freq 10 \
  --srcdict data/eiopa/1_external/dict.iwslt.en \
#  --alignfile data/eiopa/2_interim/align.txt \