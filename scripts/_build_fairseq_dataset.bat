set ID=1689
set DIRECTORY=data/eiopa/5_model_input
set FILE=%DIRECTORY%/data_%ID%
set OUT_DIR=data/eiopa/5_model_input

fairseq-preprocess -s nl -t ql ^
  --trainpref %FILE%-train --validpref %FILE%-val --testpref %FILE%-test_1 ^
  --destdir %OUT_DIR%/fairseq-data-bin-%ID% ^
  --cpu --empty-cache-freq 10
