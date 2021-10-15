Neural Query Machine
==============================

A Transformer-based Machine for answering questions on insurance companies converted to RDF

--------

Start Project
-------------

Clone the repository using the following command:
```
git clone --recurse-submodules https://github.com/DeNederlandscheBank/nqm.git
```

### Prerequisites

- Python version >= 3.6
- Numpy version == 1.19.x

### Create virtual environment

It is advisable to use a virtual environment for this project. One option is
to use conda:

```
conda env create -f environment_cross_platform.yml
conda activate fairseq_local
pip install subword_nmt
pip install --editable ./fairseq
```

When working on this project using MacOS, working with the conda environment
has been more stable. When you want to use jupyter notebooks, then `nb_conda`
has to be installed additionally.

Another option is to use pip together with your favourite virtual environment
application.

    pip install -r requirements.txt
    pip install --editable ./fairseq

First installing the 'requirements.txt' including pytorch amongst others and
then 'fairseq' separately prevents possible issues with Intel OpenMP library.

__Remark__: The source code in this repo is compatible with the version of fairseq from the 
following repo (https://github.com/jm-glowienke/fairseq). This repo has some adjustments for using the replacement, 
pointer-generator and alignment model.

To install fairseq properly, please use: git clone --recurse-submodules https://github.com/jm-glowienke/fairseq

Via the Python Package Index, version 0.10.2 is available at the moment. However, in 
the meantime the storing and saving of checkpoints has been adapted in fairseq and is not
backwards compatible to 0.10.2. With a 
new update of the PyPI version, it might be possible to use to the version installed with pip. Please pay attention 
that for certain models, the corresponding model file needs to be placed in the correct directory.

## Template files

The repo contains a set of templates for the EIOPA dataset. More templates can be added to the template files or you 
can make completely new ones when adapting the code to a new graph database.

Each template must consist out of a question, the query to get this information and a generator query to fill the 
placeholders with entity names from the database. These elements need to be seperated by a semi-colon and stored in 
a `.csv` file. It is possible to fill multiple placeholders in the query, but carefully check whether there is not a 
mix up between the placeholders with information.

Test files should be placed in a folder for faster generation using the '--folder' option of the generator. The files
in the folder must have unique identifier, e.g. an integer, at the fifth-last position, e.g. "test_5.csv".

## Run queries on EIOPA and GLEIF database:

For running queries on the database, you can use one of the jupyter notebooks in the `notebooks` folder. Please 
ensure to install `nb_conda` and select the correct kernel in the notebook to run the queries smoothly.


## Pipeline for preparing data and running model

There are three different data generation scripts present in folder `scripts`:

- `data_eiopa_pg.sh`: Generate data to use with a pointer-generator model
- `data_eiopa_subwords.sh`: Generates data with or without subwords
- `data_eiopa_xlmr.sh`: Generates data to use with the XLMR-R language model

The scripts should be run from root. For each script, at the top a couple parameters are defined in capital letters, 
which enable using slightly varied setups.

### Train model:

For every model used during research, a script is available to train the particular model. It is advisable to do 
this on a platform with enough computation power. Don't forget to adapt the data ID to your dataset!

### Evaluate model:

There are three different data generation scripts present in folder `scripts`. The scripts can be run with 
parameters given from the command line as input or at the top of the scripts. They are incorporated in the data 
training scripts with the correct setup.

- `_fairseq_evaluation_align.sh`: Evaluate a model using the test sets with replacing the out-of-vocabulary words in 
  the target sequence by the aligned word of the source sequence
- `_fairseq_evaluation_pg.sh`: Evaluate a pointer-generator model
- `_fairseq_evaluation_subwords.sh`: Evaluate model with subwords, can also be adapted to non-subword model


### Interactive use:

You can also interactively evaluate models using `src/interactive_translation.py` and even directly the database 
using your questions. The script can be used with all models trained originally by given the letter as parameter.
An alternative is to use the chatbot: https://github.com/DeNederlandscheBank/nqm-bot

```shell
python3 src/interactive_translation.py --model {MODEL-LETTER}
```

## Working with submodules

To ensure a proper-working system and staying up-to-date, run the command below:
```
git pull origin --recurse-submodules
git submodule update --init --merge --recursive --remote
```
This command pulls all the upstream changes including for the submodules.
You can find more info on submodules via https://git-scm.com/book/en/v2/Git-Tools-Submodules

## Adapting the database

The script `scripts/create_EIOPA_triples.py` makes it possible to re-generated the EIOPA RDF dataset an perform 
changes to the graph database. The code can also serve as inspiration to add new datasets to the graph database.
