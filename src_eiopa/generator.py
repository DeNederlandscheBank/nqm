#!/usr/bin/env python
"""

Generator module for EIOPA and GLEIF register data

Jan-Marc Glowienke

"""
import argparse
import collections
import importlib
import io
import logging
import os
import sys
import traceback

from rdflib import term, Graph
from sacremoses import MosesTokenizer
from tqdm import tqdm

try:
    from generator_utils import strip_item, sparql_encode, \
    read_template_file, add_quotation_marks
except:
    from nqm.src_eiopa.generator_utils import strip_item, sparql_encode, \
    read_template_file, add_quotation_marks

EXAMPLES_PER_TEMPLATE = 100


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
    """ Returns list of query results """
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


def build_dataset_pair(item, template, mt):
    """ Taken from LiberAi
    Returns dataset_pair with query and natural language question
    Currently only able to work with one variable
    Natural language question is tokenized using Moses and joined back to
    1 string with all tokens seperated by ' '.
    Queries are tokenized using a special hand-made tokenizer.
     """
    natural_language = getattr(template, 'question')
    query = getattr(template, 'query')

    for cnt, variable in enumerate(template.variables):
        placeholder = "<{}>".format(str.upper(variable))
        if placeholder in natural_language:
            item_nl = strip_item(item[cnt])
            natural_language = natural_language.replace(placeholder, item_nl)
            natural_language = ' '.join(mt.tokenize(natural_language))
        if placeholder in query:
            item_ = add_quotation_marks(strip_item(item[cnt]))
            query = query.replace(placeholder, item_)
    query = sparql_encode(query)
    dataset_pair = { 'natural_language': natural_language,
                     'query': query }
    return dataset_pair


def generate_dataset(templates, output_dir, file_mode, job_id,
                     type_, mt, graph_database):
    """
        This function will generate dataset from the given templates and
        store it to the output directory.
        :param graph_database:
    """
    cache = dict()
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    it = 0
    with io.open(output_dir + '/data_{1}-{0}.nl'.format(type_, job_id),
                 file_mode, encoding="utf-8") as nl_questions, \
            io.open(output_dir + '/data_{1}-{0}.ql'.format(type_, job_id),
                    file_mode, encoding='utf-8') as queries:
        for template in tqdm(templates):
            it = it + 1
            try:
                # get list of results for generator_query
                results = get_results_of_generator_query(cache, template,
                                                         graph_database)
                if results is None:
                    logging.debug("no data for {}".format(template.question))
                    not_instanced_templates.update([template.question])
                    continue

                for item in results:
                    dataset_pair = build_dataset_pair(item, template, mt)

                    if dataset_pair is not None:
                        nl_questions.write("{}\n"
                            .format(
                            dataset_pair['natural_language']))

                        queries.write("{}\n".format(dataset_pair['query']))

            except:
                exception = traceback.format_exc()
                logging.error('template {} caused exception {}'.format(
                    getattr(template, 'id'), exception))
                logging.info(
                    '1. fix problem\n2. remove templates until the exception \
                     template in the template file\n3. restart with `-- \
                     continue` parameter')
                raise Exception()


def get_results_of_generator_query(cache, template, graph_database):
    """
    Return list of items to fill placeholder in template query by
    using the generator_query.
    Only returns results if sufficient amount of items was found, otherwise
    returns "None". The threshold is defined by EXAMPLES_PER_TEMPLATE
    :param graph_database:
    """
    generator_query = template.generator_query
    results = None

    # print("Get_results: Generator_query: ",generator_query)
    def attempt_one(template):
        return prepare_generator_query(template)

    def attempt_two(template):
        return prepare_generator_query(template, add_type_requirements=False)

    for attempt, prepare_query in enumerate([attempt_one, attempt_two],
                                            start=1):
        generator_query = prepare_query(template)

        if generator_query in cache:
            results = cache[generator_query]
            break
        logging.debug('{}. attempt generator_query: {}'.format(attempt,
                                                               generator_query))
        results = query_database(generator_query, graph_database)
        # print("Get_results: Results:\n ",results)
        if len(results) >= EXAMPLES_PER_TEMPLATE:
            cache[generator_query] = results
            break
    return results


def prepare_generator_query(template, add_type_requirements=True):
    """
    This function prepares the generator query to be used to query the
    database.
    At the moment, it is performing no action
    """
    generator_query = getattr(template, 'generator_query')
    target_classes = getattr(template, 'target_classes')
    variables = getattr(template, 'variables')

    return generator_query


if __name__ == '__main__':
    """
        (MG): take in arguments for execution of generator:
        continue: use to continue after exception happened
        templates (required): start file, templates for directionary
        output (required): output directory
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', dest='use_folder',
                        metavar='template_folder',
                        help='use folder for templates')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('--templates', dest='templates',
                               metavar='templateFile', help='templates',
                               required=True)  # This should be a directory
    # when 'folder' option is used.
    requiredNamed.add_argument(
        '--output', dest='output', metavar='outputDirectory',
        help='dataset directory', required=True)
    requiredNamed.add_argument(
        '--id', dest='id', metavar='identifier', help='job identifier',
        required=True)
    requiredNamed.add_argument(
        '--type', dest='type', metavar='filetype', required=True,
        help='type of templates: train/val or test_x'
    )
    requiredNamed.add_argument(
        '--graph-data-path', dest='graph_data_path',
        required=True, help='path to folder containing graph data'
    )
    requiredNamed.add_argument(
        '--input-language', dest='input_lang',
        required=True, help="input language as abbreviation"
    )

    args = parser.parse_args()

    template_file = args.templates
    output_dir = args.output
    job_id = args.id
    type_ = args.type
    use_resources_dump = False  # args.continue_generation # (MG): Value is TRUE
    # when continuing on existing dump
    use_folder = args.use_folder

    # (MG): Initiate logging file
    logging.basicConfig(
        filename='{}/logs/generator_{}.log'.format(output_dir, job_id),
        level=logging.DEBUG)
    """
    # (MG): Check whether there exitst already some resources to be used
    # (MG): from previous run probably
    resource_dump_file = output_dir + '/resource_dump.json'
    resource_dump_exists = os.path.exists(resource_dump_file)

    # print resource_dump_file, resource_dump_exists =>\
    # data/place_v1/resource_dump.json False

    # (MG): If dump file already exists, when it shouldn't, then EXEMPTION
    if (resource_dump_exists and not use_resources_dump):
        warning_message = 'Warning: The file {} exists which indicates an error.\
        Remove file or continue generation after fixing with --continue'.format(
            resource_dump_file)
        print(warning_message)
        sys.exit(1)
    """
    importlib.reload(sys)

    # (MG): initiate file for collection of templates
    not_instanced_templates = collections.Counter()
    # (MG): create collection for used_resources or empty collection
    # used_resources = collections.Counter(json.loads(open(
    #     resource_dump_file).read())) if use_resources_dump \
    #     else collections.Counter()
    used_resource = collections.Counter()
    file_mode = 'a' if use_resources_dump else 'w'  # (MG): append vs write
    graph_database = initialize_graph(args.graph_data_path)

    moses_tokenizer = MosesTokenizer(lang=args.input_lang)

    try:
        if args.use_folder is not None:
            print("Using folder for templates")
            files = os.listdir(os.path.join(template_file, use_folder))
            for file in files:
                file_type = type_ + "_" + file[-5]
                print("Generating file: {}".format(file_type))
                templates = read_template_file(os.path.join(
                    template_file, use_folder, file))
                generate_dataset(templates, output_dir, file_mode, job_id,
                                 file_type, moses_tokenizer, graph_database)
        else:
            templates = read_template_file(template_file)
            generate_dataset(templates, output_dir, file_mode, job_id, type_,
                             moses_tokenizer, graph_database)
    except:  # (MG): exception occured
        print('exception occured, look for error in log file')
        # save_cache(resource_dump_file, used_resources)
    else:  # (MG): no exception happened
        print("Success for generator!")
        # save_cache(
        #     '{}/logs/used_resources_{}.json'.format(output_dir, job_id),\
        #      used_resources)
    # finally: # (MG): always execute this
    #     log_statistics(used_resources, SPECIAL_CLASSES,
    #                    not_instanced_templates)
