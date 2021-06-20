#!/usr/bin/env python
"""

Neural SPARQL Machines - Generator utils.

Adapted to new dataset by Jan-Marc Glowienke

'SPARQL as a Foreign Language' by Tommaso Soru and Edgard Marx et al.,
    SEMANTiCS 2017
https://arxiv.org/abs/1708.07624

Version 1.0.0

Docstrings and comments added by Jan-Marc Glowienke (MG)

"""
import logging
import re


def strip_item(s):
    # s = re.sub(r'\([^)]*\)', '', s) # removes everything inside brackets
    # s = re.sub(r'"', '', s)
    s = re.sub(r'[()\[\],"]', '', s)  # removes all types of brackets and quotes
    # if "," in s:
    #     s = s[:s.index(",")]
    return s.strip().lower()


def add_quotation_marks(s):
    return '"' + s + '"'


REPLACEMENTS = [
    ['dbo:', 'http://dbpedia.org/ontology/', 'dbo_'],
    ['dbp:', 'http://dbpedia.org/property/', 'dbp_'],
    ['dbc:', 'http://dbpedia.org/resource/Category:', 'dbc_'],
    ['dbr:', 'res:', 'http://dbpedia.org/resource/', 'dbr_'],
    ['dct:', 'dct_'],
    ['geo:', 'geo_'],
    ['georss:', 'georss_'],
    ['rdf:', 'rdf_'],
    ['rdfs:', 'rdfs_'],
    ['foaf:', 'foaf_'],
    ['owl:', 'owl_'],
    ['yago:', 'yago_'],
    ['skos:', 'skos_'],
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


def sparql_encode(sparql):
    encoded_sparql = do_replacements(sparql)
    return encoded_sparql


def sparql_decode(encoded_sparql):
    decoded_sparql = reverse_replacements(encoded_sparql)
    return decoded_sparql


def do_replacements(sparql):
    """
    (MG): Replace signs by encoding words in the query, e.g. "(" becomes
    bracket_open. Simplify learning for translation.
    """
    for r in REPLACEMENTS:
        encoding = r[-1]
        for original in r[:-1]:
            sparql = sparql.replace(original, encoding)
    return sparql


def reverse_replacements(sparql):
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
            # (MG): "or None" keeps length of list flexible
            question = values[0]
            query = values[1]
            generator_query = values[2]
            id_number = values[3] if (len(values) >= 4 and values[3]) \
                else line_number
            line_number += 1
            if check_variable_placeholder_match(question, query,
                                                generator_query) is True:
                annotation = Annotation(question, query, generator_query,
                                        id_number)
                annotations.append(annotation)
    return annotations


# (MG): save templates as annotation object
class Annotation:
    def __init__(self, question, query, generator_query, id_number=None):
        self.question = question
        self.query = query
        self.generator_query = generator_query
        self.id = id_number
        self.variables = extract_variables(generator_query)


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
    """ Check whether placeholders in query and question have a corresponding
    variable in the generator_query """
    tmp = True
    for variable in extract_variables(generator_query):
        if f"<{str.upper(variable)}>" not in query:
            logging.error(f'Question {question}: There is no placeholder for '
                          f'variable {variable} in the query. Skipping '
                          f'this template!')
            tmp = False
        if f"<{str.upper(variable)}>" not in question:
            logging.error(f'Question {question}: There is no placeholder for '
                          f'variable {variable} in the question. Skipping '
                          f'this template!')
            tmp = False
    return tmp
