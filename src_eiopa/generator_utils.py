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
import collections
import json
import logging
import re
from functools import reduce


def log_statistics(used_resources, special_classes, not_instanced_templates):
    total_number_of_resources = len(used_resources)
    total_number_of_filled_placeholder_positions = sum(used_resources.values())
    examples_per_instance = collections.Counter()
    for resource in used_resources:
        count = used_resources[resource]
        examples_per_instance.update([count])

    logging.info('{:6d} used resources in {} placeholder positions'.format(
        total_number_of_resources,
        total_number_of_filled_placeholder_positions))
    for usage in examples_per_instance:
        logging.info(
            '{:6d} resources occur \t{:6d} times \t({:6.2f} %) '.format(
                examples_per_instance[usage], usage,
                examples_per_instance[usage] * 100 / total_number_of_resources))
    for cl in special_classes:
        logging.info(
            '{} contains: {}'.format(cl, ', '.join(special_classes[cl])))
    logging.info('{:6d} not instanciated templates:'.format(
        sum(not_instanced_templates.values())))
    for template in not_instanced_templates:
        logging.info('{}'.format(template))


def save_cache(file, cache):
    ordered = collections.OrderedDict(cache.most_common())
    with open(file, 'w') as outfile:
        json.dump(ordered, outfile)


def strip_item(s):
    # s = re.sub(r'\([^)]*\)', '', s) # removes everything inside brackets
    # s = re.sub(r'"', '', s)
    s = re.sub(r'[()\[\],"\']', '', s) # removes all types of brackets and quotes
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
    shorter_encoded_sparql = shorten_query(encoded_sparql)
    return shorter_encoded_sparql


def sparql_decode(encoded_sparql):
    short_sparql = reverse_replacements(encoded_sparql)
    sparql = reverse_shorten_query(short_sparql)
    return sparql


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


def shorten_query(sparql):
    sparql = re.sub(r'order by desc\s+....?_open\s+([\S]+)\s+....?_close',
                    '_obd_ \\1', sparql, flags=re.IGNORECASE)
    sparql = re.sub(r'order by asc\s+....?_open\s+([\S]+)\s+....?_close',
                    '_oba_ \\1', sparql, flags=re.IGNORECASE)
    sparql = re.sub(r'order by\s+([\S]+)', '_oba_ \\1', sparql,
                    flags=re.IGNORECASE)
    return sparql


def reverse_shorten_query(sparql):
    sparql = re.sub(r'_oba_ ([\S]+)', 'order by asc (\\1)', sparql,
                    flags=re.IGNORECASE)
    sparql = re.sub(r'_obd_ ([\S]+)', 'order by desc (\\1)', sparql,
                    flags=re.IGNORECASE)
    return sparql


# (MG): read in template file, required structure noted in readme.md
def read_template_file(file):
    annotations = list()
    line_number = 1
    with open(file) as f:
        for line in f:
            values = line.strip("\n").split(';')
            target_classes = [values[0] or None, values[1] or None,
                              values[2] or None]
            # (MG): "or None" keeps length of list flexible
            question = values[3]
            query = values[4]
            generator_query = values[5]
            id_ = values[6] if (len(values) >= 7 and values[6]) else line_number
            line_number += 1
            annotation = Annotation(
                question, query, generator_query, id_, target_classes)
            annotations.append(annotation)
    return annotations


# (MG): save templates as annotation object
class Annotation:
    def __init__(self, question, query, generator_query,
                 id_=None, target_classes=None):
        self.question = question
        self.query = query
        self.generator_query = generator_query
        self.id = id_
        self.target_classes = target_classes if target_classes is not None \
            else []
        self.variables = extract_variables(generator_query)


# (MG): find variables in query by checking for the variable pattern symbols
# (MG): not sure how this pattern exactly works, but will have to trust the code
# (MG): this however could give problem for own templates
def extract_variables(query):
    variables = []
    query_form_pattern = r'^.*?where'
    query_form_match = re.search(query_form_pattern, query, re.IGNORECASE)
    if query_form_match:
        letter_pattern = r'\?(\w)'
        variables = re.findall(letter_pattern, query_form_match.group(0))
    return variables


def extract_encoded_entities(encoded_sparql):
    sparql = sparql_decode(encoded_sparql)
    entities = extract_entities(sparql)
    encoded_entities = list(map(sparql_encode, entities))
    return encoded_entities


def extract_entities(sparql):
    triples = extractTriples(sparql)
    entities = set()
    for triple in triples:
        possible_entities = [triple['subject'], triple['object']]
        sorted_out = [e for e in possible_entities if
                      not e.startswith('?') and ':' in e]
        entities = entities.union(
            [re.sub(r'^optional{', '', e, flags=re.IGNORECASE) for e in
             sorted_out])
    return entities


def extract_predicates(sparql):
    triples = extractTriples(sparql)
    predicates = set()
    for triple in triples:
        pred = triple['predicate']
        predicates.add(pred)
    return predicates


def extractTriples(sparqlQuery):
    triples = []
    whereStatementPattern = r'where\s*?{(.*?)}'
    whereStatementMatch = re.search(whereStatementPattern, sparqlQuery,
                                    re.IGNORECASE)
    if whereStatementMatch:
        whereStatement = whereStatementMatch.group(1)
        triples = splitIntoTriples(whereStatement)
    return triples


def splitIntoTriples(whereStatement):
    tripleAndSeparators = re.split(r'(\.[\s\?\<$])', whereStatement)
    trimmed = [str.strip() for str in tripleAndSeparators]

    def repair(list, element):
        if element not in ['.', '.?', '.<']:
            previousElement = list[-1]
            del list[-1]
            if previousElement in ['.', '.?', '.<']:
                cutoff = previousElement[1] if previousElement in ['.?',
                                                                   '.<'] else ''
                list.append(cutoff + element)
            else:
                list.append(previousElement + ' ' + element)
        else:
            list.append(element)

        return list

    tripleStatements = reduce(repair, trimmed, [''])
    triplesWithNones = list(map(splitIntoTripleParts, tripleStatements))
    triples = [triple for triple in triplesWithNones if triple != None]
    return triples


def splitIntoTripleParts(triple):
    statementPattern = r'(\S+)\s+(\S+)\s+(\S+)'
    statementPatternMatch = re.search(statementPattern, triple)

    if statementPatternMatch:
        return {
            'subject': statementPatternMatch.group(1),
            'predicate': statementPatternMatch.group(2),
            'object': statementPatternMatch.group(3)
        }
    else:
        return None


def fix_URI(query):
    query = re.sub(r"dbr:([^\s]+)", r"<http://dbpedia.org/resource/\1>", query)
    if query[-2:] == "}>":
        query = query[:-2] + ">}"
    return query
