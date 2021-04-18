set ID=1689
set IN_DIR=data/eiopa/5_model_input
set MODEL_DIR=models/transformer_iwslt_de_en_%ID%

fairseq-train %IN_DIR%/fairseq-data-bin-%ID% ^
 -a transformer_iwslt_de_en --optimizer adam --lr 0.0005 -s nl -t ql ^
 --tensorboard-logdir %MODEL_DIR%/out_%ID%/ ^
 --label-smoothing 0.1 --dropout 0.3 --max-tokens 4000 ^
 --min-lr "1e-09" --lr-scheduler inverse_sqrt --weight-decay 0.0001 ^
 --criterion label_smoothed_cross_entropy --scoring bleu ^
 --warmup-updates 4000 --warmup-init-lr "1e-07" ^
 --max-epoch 5 --save-interval 1 --valid-subset valid ^
 --adam-betas "(0.9, 0.98)" --save-dir %MODEL_DIR% ^
 --batch-size 128 --keep-best-checkpoints 1 --patience 50 ^
 --eval-bleu ^
  --eval-bleu-args "{""beam"": 5}" ^
  --eval-bleu-detok space ^
  --eval-bleu-remove-bpe ^
  --best-checkpoint-metric bleu --maximize-best-checkpoint-metric
