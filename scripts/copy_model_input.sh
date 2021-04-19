#!/bin/bash

# Use this script from the root!
# This script copies the required model files using $ID and places them in the
# correct directory. The name is adapated using $ID_new. These two variables
# have to be adapted to the desired values.
ID=19-04_11-53_663
ID_NEW=663

DATA_DIR=data/eiopa/3_processed
VOC_DIR=data/eiopa/4_vocabularies
TGT_DIR=data/eiopa/5_model_input
COUNT_TEST=$((`ls -l data/eiopa/1_external/test_templates/*.csv | wc -l` -1 ))


# Copy language pairs to correct folder
for L in nl ql; do
    for f in train.$L val.$L test_{1..$COUNT_TEST}.$L; do
        echo "copying ${f}..."
        cp -R $DATA_DIR/data_"$ID"-$f $TGT_DIR/data_"$ID_NEW"-$f
    done
done

# Copy helper files
cp -R $VOC_DIR/$ID-bpe.codes $TGT_DIR/$ID_NEW-bpe.codes