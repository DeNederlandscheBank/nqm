This folder contains scripts, which can be run from root independently. Mostly,
previous to running it, the data ID needs to be corrected.


__Model Overview:__
- A: IWSLT_de_en transformer, no subwords used, all names known (11468)
- B: IWSLT_de_en transformer, subwords, names unknown (4614)
- C: IWSLT_de_en transformer, subwords, names unknown and known (30387)
- D: A using alignment model and replace_unk
- E: B using alignment model and replace_unk
- F: C using alignment model and replace_unk
- G: Pointer-generator model with known and unknown names (19480)
- H: Pointer-generator model with unknown names (9881)
