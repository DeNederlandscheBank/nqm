In this folder, the original XLMR.base model should be stored, if needed for
fine-tuning the XLMR model.

### How to download XLMR.base
Replace `{root}` by the path to the root or just the folder of your local copy 
of the git repository.
```
cd {root}/models/xlmr.base
wget https://dl.fbaipublicfiles.com/fairseq/models/xlmr.base.tar.gz
# unpack the archive
tar -xzvf xlmr.base.tar.gz 

# move model file out of nested folder
mv xlmr.base/model.pt model.pt 
# remove nested folder, helper files are contained in data/eiopa/1-external
rm -r xlmr.base
rm xlmr.base.tar.gz
```
After following the steps above, this folder should only contain the `model.pt` checkpoint
file and this `README.md`.