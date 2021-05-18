ID=25028 # find in build script or end of fairseq-data-bin

if [ -n "$1" ]
    then ID=$1
fi

IN_DIR=data/eiopa/5_model_input
MODEL_DIR=models/transformer_iwslt_de_en_$ID

fairseq-train $IN_DIR/fairseq-data-bin-$ID \
 -a transformer_pointer_generator_iwslt_de_en --optimizer adam --lr 0.0005 -s nl -t ql \
 --save-dir $MODEL_DIR --batch-size 4000