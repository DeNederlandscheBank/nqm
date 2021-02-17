Neural Query Machine
==============================

A LSTM-based Machine for answering questions on XBRL instances converted to RDF

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------

Start Project
-------------

### Install packages

At the root:

    pip install -r requirements.txt


### Change the build_vocap.py file

We need to change the build_vocab.py file to get it working. In order to do that you have to change that file in the location that pip stored it in. This will probably be somewhere in anaconda3\envs\your_env_name\lib\site-packages\onmt\bin\build_vocab.py. You can however also run the bat file below and use this to find the file (it will show in the error). Here you have to change line 46 to:

     with open(save_path, "w",  encoding="utf-8") as fo:



### Desired structure for template data

The generator.py for the dictionaries expects the following structure for the template:

    target_class; target_class; target_class; question; query; generator_query; id

The target_class are treated to belong to one variable in the query(MG: not 100% sure about this yet). The target_class variables and Id are optional. In case no ID is given for a template, the line number will be taken as ID.

The templates should be given in a .csv file with each line being a template.

### Pipeline for preparing data and running model

Open your git bash:

    cd src/

    pipeline.bat



### Test your model:

In your bash:

    onmt_translate -model ../../models/model_step_10000.pt -src ../../data/processed/test_en.txt -output ../../data/processed/test_sparql_model.txt


Note that onmt_translate is written as:

    onmt_translate -model path_to_saved_model/model -src path_to_input_text/text -output path_to_output/file


If you want to decode the output of the test files into more of an sparql output:

    python decode_lines.py



<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
