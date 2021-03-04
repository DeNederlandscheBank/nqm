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
    """ Taken from LiberAi """
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
    dataset_pair = {'english': english, 'sparql': sparql}
    return dataset_pair





if __name__ == '__main__':
    """
        (MG): take in arguments for execution of generator:
        continue: use to continue after exception happened
        templates (required): start file, templates for directionary
        output (required): output directory
    """
    parser = argparse.ArgumentParser()
    # parser.add_argument('--continue', dest='continue_generation',
                        action='store_true', help='Continue after exception')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('--templates', dest='templates',
                               metavar='templateFile', help='templates',
                                required=True)
    requiredNamed.add_argument(
        '--output', dest='output', metavar='outputDirectory',
        help='dataset directory', required=True)
    args = parser.parse_args()

    template_file = args.templates
    output_dir = args.output
    use_resources_dump = args.continue_generation # (MG): Value is TRUE when
    # continuing on existing dump

   # print use_resources_dump => False

   # (MG): Initiate logging file
    time = datetime.datetime.today()
    logging.basicConfig(
        filename='{}/logs/generator_{:%Y-%m-%d-%H-%M}.log'.format(output_dir, time), level=logging.DEBUG)

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

    importlib.reload(sys)

    # (MG): initiate file for collection of templates
    not_instanced_templates = collections.Counter()
    # (MG): create collection for used_resources or empty collection
    used_resources = collections.Counter(json.loads(open(
        resource_dump_file).read())) if use_resources_dump \
        else collections.Counter()
    file_mode = 'a' if use_resources_dump else 'w' # (MG): append vs write
    templates = read_template_file(template_file)

    try:
        generate_dataset(templates, output_dir, file_mode)
    except: # (MG): exception occured
        print('exception occured, look for error in log file')
        save_cache(resource_dump_file, used_resources)
    else:  # (MG): no exception happened
        save_cache(
            '{}/used_resources_{:%Y-%m-%d-%H-%M}.json'.format(output_dir, time),\
             used_resources)
    finally: # (MG): always execute this
        log_statistics(used_resources, SPECIAL_CLASSES,
                       not_instanced_templates)
