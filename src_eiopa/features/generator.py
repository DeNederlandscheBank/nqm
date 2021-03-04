#!/usr/bin/env python
"""

Generator module for EIOPA and GLEIF register data

Jan-Marc Glowienke

"""
import argparse
import collections
import datetime
import json
import logging
import operator
import os
import random
import re
import sys
import traceback
from tqdm import tqdm
import io

from generator_utils import log_statistics, save_cache, query_dbpedia,\
 strip_brackets, encode, read_template_file
import importlib

EXAMPLES_PER_TEMPLATE = 100


def build_dataset_pair(binding, template):
    """ Taken from LiberAi
    Returns dictionary with query and natural language question
     """
    english = getattr(template, 'question')
    sparql = getattr(template, 'query')
    for variable in binding:
        uri = binding[variable]['uri']
        label = binding[variable]['label']
        placeholder = '<{}>'.format(str.upper(variable))
        if placeholder in english and label is not None:
            english = english.replace(placeholder, strip_brackets(label))
        if placeholder in sparql and uri is not None:
            sparql = sparql.replace(placeholder, uri)

    sparql = encode(sparql)
    dataset_pair = {'natural_language': english, 'query': sparql}
    return dataset_pair

def generate_dataset(templates,output_dir,file_mode,job_id):
    """
        This function will generate dataset from the given templates and
        store it to the output directory.
    """
    cache = dict()
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    it = 0
    with io.open(output_dir + '/data_nl-{}.txt'.format(job_id), file_mode,\
                encoding = "utf-8") as nl_questions,\
         io.open(output_dir + '/data_ql-{}.txt'.format(job_id),file_mode,\
                encoding='utf-8') as queries:
        for template in tqdm(templates):
            it = it + 1
            try:
                # get list of results for generator_query
                results = get_results_of_generator_query(cache,template)
                if results is None:
                    logging.debug("no data for {}".format(template.question))
                    not_instanced_templates.update([template.question])
                    continue

                for item in results:
                    dataset_pair = build_dataset_pair(item,template)

                    if dataset_pair:
                        # dataset_pair['natural_language'] = " ".join(
                        #     dataset_pair['natural_language'].split())
                        nl_questions.write("{}\n"\
                                .format(dataset_pair['natural_language']))

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

def get_results_of_generator_query(cache,template):
    """
    Return list of items to fill placeholder in template query by
    using the generator_query
    """
    return False


if __name__ == '__main__':
    """
        (MG): take in arguments for execution of generator:
        continue: use to continue after exception happened
        templates (required): start file, templates for directionary
        output (required): output directory
    """
    parser = argparse.ArgumentParser()
    # parser.add_argument('--continue', dest='continue_generation',
                        # action='store_true', help='Continue after exception')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('--templates', dest='templates',
                               metavar='templateFile', help='templates',
                                required=True)
    requiredNamed.add_argument(
        '--output', dest='output', metavar='outputDirectory',
        help='dataset directory', required=True)
    requiredNamed.add_argument(
        '--id', dest='id', metavar = 'identifier', help = 'job identifier',
        required = True)
    args = parser.parse_args()

    template_file = args.templates
    output_dir = args.output
    job_id = args.id
    use_resources_dump = False #args.continue_generation # (MG): Value is TRUE when
    # continuing on existing dump

   # (MG): Initiate logging file
    logging.basicConfig(
        filename='{}/logs/generator_{}.log'.format(output_dir, job_id), level=logging.DEBUG)
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
    file_mode = 'a' if use_resources_dump else 'w' # (MG): append vs write
    templates = read_template_file(template_file)

    try:
        generate_dataset(templates, output_dir, file_mode, job_id)
    except: # (MG): exception occured
        print('exception occured, look for error in log file')
        # save_cache(resource_dump_file, used_resources)
    else:  # (MG): no exception happened
        save_cache(
            '{}/logs/used_resources_{}.json'.format(output_dir, job_id),\
             used_resources)
    # finally: # (MG): always execute this
    #     log_statistics(used_resources, SPECIAL_CLASSES,
    #                    not_instanced_templates)
