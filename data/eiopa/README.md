The folder __1_external__ contains data from EIOPA register for European insurance companies and the accompanying GLEIF identifier data.

Furthermore, there are several files containing templates to build the dataset for training the translation model:

__Templates_train_val__: set of templates, consisting of a natural language question, the corresponding SPARQL query and a generator query to generate the dataset

__templates_test_1__: Question is not seen before, but query should be known

__templates_test_2__: new query, which is combination of elements in train/validation queries; extra difficulty: looks for two variables

__templates_test_3__: question and queries were seen before, but new names. This achieved by not only selecting dutch insurances, but from whole Europe
