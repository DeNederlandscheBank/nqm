#!/usr/bin/env python
"""

Generator module to generate language dataset base on
graph database containing EIOPA and GLEIF register data

Jan-Marc Glowienke, Intern at De Nederlandsche Bank 2021

Best way to use this module is using a data script in the scripts folder
of this repo (https://github.com/DeNederlandscheBank/nqm/)
Use a new unique ID everytime the script is run!

This module is based on the following paper
'SPARQL as a Foreign Language' by Tommaso Soru et al., SEMANTiCS 2017
https://arxiv.org/abs/1708.07624
and the accompanying github repo (https://github.com/LiberAI/NSpM/), licensed
under the MIT license.
"""
import argparse
import importlib
import io
import logging
import os
import random
import sys
import traceback

from rdflib import term, Graph
from sacremoses import MosesTokenizer
from tqdm import tqdm

try:
    from generator_utils import strip_item, sparql_encode, \
        read_template_file, add_quotation_marks
except ImportError:  # use this when running the bot
    # noinspection PyUnresolvedReferences
    from nqm.src_eiopa.generator_utils import strip_item, sparql_encode, \
        read_template_file, add_quotation_marks


def initialize_graph(graph_data_path):
    """ Initializes the database graph and returns the graph """
    print("     Initializing Graph: This takes some time")
    eiopa_data_path = os.path.join(graph_data_path, "eiopa")
    gleif_data_path = os.path.join(graph_data_path, "gleif")

    g = Graph()
    with open(os.path.join(eiopa_data_path, 'eiopa_register.ttl'), "rb") as fp:
        g.parse(data=fp.read(), format='turtle')
    with open(os.path.join(gleif_data_path, 'gleif-L1-extract.ttl'), "rb") \
            as fp:
        g.parse(data=fp.read(), format='turtle')
    with open(os.path.join(gleif_data_path, 'EntityLegalFormData.ttl'), "rb") \
            as fp:
        g.parse(data=fp.read(), format='turtle')
    print("Graph has {} statements.".format(len(g)))
    logging.debug("Graph has {} statements.".format(len(g)))
    return g


def query_database(query, graph):
    """ Returns list of list of query results """
    results = []
    for row in graph.query(query):
        items = []
        for item in row:
            items.append(str(get_name(item)))
        results.append(items)
    return results


def get_name(uri):
    """ Visualize the name of uri without namespace. Taken from Willem Jan """
    if isinstance(uri, term.URIRef):
        return uri.n3().split("/")[-1][0:-1]
    else:
        return uri


def build_dataset_quadruple(items, template, mt):
    """ (LiberAI inspired)
    Returns dataset_quadruple with query and natural language question
    Natural language question is tokenized using Moses and joined back to
    1 string with all tokens seperated by ' '.
    Queries are tokenized using a special-made tokenizer.

    This function should work for filling multiple placeholders, but this
    was not tested (21-06-2021) and there might be a mix-up, i.e. value for
    variable a is filled for placeholder <B> and vice-versa.
     """
    natural_language = getattr(template, 'question')
    query = getattr(template, 'query')
    natural_language_raw = getattr(template, 'question')
    query_raw = getattr(template, 'query')

    # When reading in templates, we ensure there is at least one variable in
    # the generator_query
    # Modifying the query and question step by step for each variable
    for cnt, variable in enumerate(template.variables):
        placeholder = "<{}>".format(str.upper(variable))
        # We ensure that placeholder is present in question and query
        # when reading in the templates, so actually if statement is not
        # necessary, but keep it to prevent bugs occurring.
        if placeholder in natural_language:
            # replace placeholder by stripped item (no special symbols)
            item_nl = strip_item(items[cnt])
            natural_language_filled = natural_language.replace(placeholder,
                                                               item_nl)
            natural_language_not_filled = natural_language.replace(placeholder,
                                                                   " ")
            # tokenize the question and join back together
            natural_language = ' '.join(mt.tokenize(natural_language_filled))
            natural_language_raw = ' '.join(
                mt.tokenize(natural_language_not_filled))
        if placeholder in query:
            item = add_quotation_marks(strip_item(items[cnt]))
            query_raw = query.replace(placeholder, 'quot_mark_l quot_mark_r')
            query = query.replace(placeholder, item)
    query = sparql_encode(query)
    query_raw = sparql_encode(query_raw)
    dataset_quadruple = {'natural_language': natural_language.lower(),
                         'query': query,
                         'query_raw': query_raw,
                         'natural_language_raw': natural_language_raw.lower()}
    return dataset_quadruple


def generate_dataset(template_collection, out_dir, job_code,
                     file_type_, mt, database, number_examples):
    """
    This function will generate dataset from the given templates and
    write it to the output directory.
    """
    logging.info(f"Building files of type: {file_type_}")
    logging.info(f"Using {number_examples} examples per template!")
    cache = dict()  # used to store results of generator_query
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    it = 0
    for template in tqdm(template_collection):
        it = it + 1
        try:
            # get list of results for generator_query, this is a list
            # of entity names or id codes
            results = get_results_of_generator_query(cache, template,
                                                     database,
                                                     number_examples)
            if results is None or len(results) == 0:
                logging.info("no data for {}".format(template.question))
                continue

            # for every found entity object, get a question and query written
            for item in results:
                dataset_quadruple = build_dataset_quadruple(item, template, mt)

                if dataset_quadruple is not None:
                    # write question and qeury filled with item to
                    # corresponding file
                    with io.open(output_dir + '/data_{1}-{0}.nl'.format(
                            file_type_, job_code), 'a', encoding="utf-8") \
                            as nl_questions, \
                            io.open(output_dir + '/data_{1}-{0}.ql'.format(
                                file_type_, job_code), 'a', encoding='utf-8') \
                            as queries:
                        nl_questions.write("{}\n".format(
                            dataset_quadruple['natural_language']))
                        queries.write("{}\n".format(dataset_quadruple['query']))
                    if 'test' not in file_type_:
                        # for train_val file, create raw files without entity
                        # objects to get dictionary without entity objects
                        with io.open(out_dir + '/data_{1}-{0}.ql.raw'.format(
                                file_type_, job_code), 'a', encoding='utf-8') \
                                as queries_raw, \
                                io.open(out_dir + '/data_{1}-{0}.nl.raw'.format(
                                    file_type_, job_code), 'a',
                                        encoding='utf-8') as nl_questions_raw:
                            queries_raw.write("{}\n".format(
                                dataset_quadruple['query_raw']))
                            nl_questions_raw.write("{}\n".format(
                                dataset_quadruple['natural_language_raw']))
        except Exception:
            exception = traceback.format_exc()
            logging.error('template {} caused exception {}'.format(
                getattr(template, 'id'), exception))
            raise Exception()


def get_results_of_generator_query(cache, template, database, examples_limit):
    """
    Return list of items to fill placeholder in template query by
    using the generator_query.
    The number of items returned is capped by EXAMPLES_PER_TEMPLATE
    """
    generator_query = template.generator_query

    # shortcut the process if generator_query was run on database before
    if generator_query in cache:
        return cache[generator_query]
    results = query_database(generator_query, database)
    random.shuffle(results)
    logging.debug('{} matches for {}'.format(len(results),
                                             getattr(template, 'id')))
    if len(results) <= examples_limit:
        return_results = results
    else:
        # reduce number of returned results to examples_limit
        return_results = results[0:examples_limit]
        cache[generator_query] = return_results
    return return_results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--folder', dest='use_folder',
        metavar='template_folder',
        help='use folder for templates')
    required_named = parser.add_argument_group('required named arguments')
    # --templates should be a directory when 'folder' option is used.
    required_named.add_argument(
        '--templates', dest='templates',
        metavar='templateFile', help='templates',
        required=True)
    required_named.add_argument(
        '--output', dest='output', metavar='outputDirectory',
        help='dataset directory', required=True)
    required_named.add_argument(
        '--id', dest='id', metavar='identifier',
        help='job identifier, which should be new and unique everytime the '
             'script is run, due to append mode',
        required=True)
    required_named.add_argument(
        '--type', dest='type', metavar='filetype', required=True,
        help='type of templates: train/val or test_x'
    )
    required_named.add_argument(
        '--graph-data-path', dest='graph_data_path',
        required=True, help='path to folder containing graph data'
    )
    required_named.add_argument(
        '--input-language', dest='input_lang',
        required=True, help="input language as abbreviation"
    )
    required_named.add_argument(
        '--examples-per-template', dest='examples_per_template',
        required=True, help='how many examples per template should be used'
    )
    args = parser.parse_args()

    template_file = args.templates
    output_dir = args.output
    job_id = args.id
    type_ = args.type
    examples_per_template = int(args.examples_per_template)
    use_folder = args.use_folder

    # (MG): Initiate logging file
    logging.basicConfig(
        filename='{}/logs/generator_{}.log'.format(output_dir, job_id),
        format='%(levelname)s - %(message)s',
        level=logging.DEBUG)
    importlib.reload(sys)

    graph_database = initialize_graph(args.graph_data_path)
    moses_tokenizer = MosesTokenizer(lang=args.input_lang)

    try:
        # if --folder is given, process all files at once in the folder
        if args.use_folder is not None:
            print("Using folder for templates")
            # check for correct use of --templates in combination with --folder
            if not os.path.isdir(template_file):
                logging.error(f'If --folder is used, parameter --templates '
                              f'needs to be a directory containing the folder '
                              f'with test templates!\n\t'
                              f'You gave {template_file} as value.')
                raise Exception
            # get all files in the folder and filter on .csv files
            files = os.listdir(os.path.join(template_file, use_folder))
            files = list(filter(lambda f: f.endswith('.csv'), files))
            for file in files:
                # get numbering, which should be at 5th last position
                # could be any identifier or symbol
                file_type = type_ + "_" + file[-5]
                print("Generating file: {}".format(file_type))
                templates = read_template_file(os.path.join(
                    template_file, use_folder, file))
                generate_dataset(templates, output_dir, job_id,
                                 file_type, moses_tokenizer, graph_database,
                                 examples_per_template)
        else:
            # standard use with one file as input via --templates
            templates = read_template_file(template_file)
            generate_dataset(templates, output_dir, job_id, type_,
                             moses_tokenizer, graph_database,
                             examples_per_template)
    except Exception:  # (MG): exception occurred
        print('exception occurred, look for error(s) in log file')
    else:  # (MG): no exception happened
        print("Success for generator! \nCheck log file for possible warnings!")
