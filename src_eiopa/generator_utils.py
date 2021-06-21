#!/usr/bin/env python
"""

Utilities, mainly for generator module

Jan-Marc Glowienke, Intern at De Nederlandsche Bank 2021

This module is based on the following paper
'SPARQL as a Foreign Language' by Tommaso Soru et al., SEMANTiCS 2017
https://arxiv.org/abs/1708.07624
and the accompanying github repo (https://github.com/LiberAI/NSpM/), licensed
under the MIT license.
"""
import logging
import re

REPLACEMENTS = [
    ['eiopa-Base:', 'eiopa_base_'],
    ['gleif-L1:', 'gleif_l1_'],
    ['gleif-Base:', 'gleif_base_'],
    ['n.v.', 'n_v'],
    ['u.a.', 'u_a'],
    ['b.v.', 'b_v'],
    [' ( ', '  par_open  '],
    [' ) ', '  par_close  '],
    ['(', ' attr_open '],
    [') ', ')', ' attr_close '],
    ['{', ' brack_open '],
    ['}', ' brack_close '],
    [' . ', ' sep_dot '],
    ['. ', ' sep_dot '],
    ['?', 'var_'],
    ['*', 'wildcard'],
    [' <= ', ' math_leq '],
    [' >= ', ' math_geq '],
    [' < ', ' math_lt '],
    [' > ', ' math_gt '],
    [' "', ' quot_mark_l '],
    ['" ', ' quot_mark_r '],
    ['"', ' quot_mark_n ']
]


# (MG): save templates as annotation object
class Annotation:
    def __init__(self, question, query, generator_query, id_number=None):
        self.question = question
        self.query = query
        self.generator_query = generator_query
        self.id = id_number
        self.variables = extract_variables(generator_query)


def strip_item(s):
    """
    removes all types of brackets and quotation marks from string object
    used to strip name objects
    """
    s = re.sub(r'[()\[\],"]', '', s)  # removes all types of brackets and quotes
    return s.strip().lower()


def add_quotation_marks(s):
    return '"' + s + '"'


def sparql_encode(sparql):
    """ encode sparql query using the replacements """
    encoded_sparql = do_replacements(sparql)
    return encoded_sparql


def sparql_decode(encoded_sparql):
    """ decode encoded sparql query by reversing the replacements """
    decoded_sparql = reverse_replacements(encoded_sparql)
    return decoded_sparql


def do_replacements(sparql):
    """
    (MG): Replace signs by encoding words in the query, e.g. "(" becomes
    bracket_open. Simplify learning for translation.
    """
    for r in REPLACEMENTS:
        encoding = r[-1]
        # several options for original are present
        for original in r[:-1]:
            sparql = sparql.replace(original, encoding)
    return sparql


def reverse_replacements(sparql):
    """ Perform reverse replacements """
    for r in REPLACEMENTS:
        original = r[0]
        encoding = r[-1]
        sparql = sparql.replace(encoding, original)
        stripped_encoding = str.strip(encoding)
        sparql = sparql.replace(stripped_encoding, original)
    return sparql


# (MG): read in template file, required structure noted in readme.md
def read_template_file(file):
    annotations = list()
    line_number = 1
    with open(file) as f:
        for line in f:
            values = line.strip("\n").split(';')
            question = values[0]
            query = values[1]
            generator_query = values[2]
            id_number = values[3] if (len(values) >= 4 and values[3]) \
                else line_number
            line_number += 1
            # only save template if variables in generator_query present
            # and there is match to the placeholders
            if check_variable_placeholder_match(question, query,
                                                generator_query) is True:
                annotation = Annotation(question, query, generator_query,
                                        id_number)
                annotations.append(annotation)
    return annotations


def extract_variables(query):
    """ find variables in query by checking for the variable pattern symbols """
    variables = []
    query_form_pattern = r'^.*?where'
    query_form_match = re.search(query_form_pattern, query, re.IGNORECASE)
    if query_form_match:
        letter_pattern = r'\?(\w)'
        variables = re.findall(letter_pattern, query_form_match.group(0))
    return variables


def check_variable_placeholder_match(question, query, generator_query):
    """
    Check whether placeholders in query and question and
    variables in the generator_query match
    """
    tmp = True
    variables = extract_variables(generator_query)

    if not variables:
        # variables is an empty list, because no variable in generator_query
        tmp = False
        logging.warning(f'Question {question}: No variables were found in the'
                        f' generator_query for this question')
    else:
        for variable in variables:
            if f"<{str.upper(variable)}>" not in query:
                logging.warning(f'Question {question}: There is no placeholder '
                                f'for variable {variable} in the query. '
                                f'Skipping this template!')
                tmp = False
            if f"<{str.upper(variable)}>" not in question:
                logging.warning(f'Question {question}: There is no placeholder '
                                f'for variable {variable} in the question. '
                                f'Skipping this template!')
                tmp = False
    return tmp
