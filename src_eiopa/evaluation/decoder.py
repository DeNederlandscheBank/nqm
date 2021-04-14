#!/usr/bin/env python
"""
copied from generator_utils
"""
import re

def sparql_decode(encoded_sparql):
    short_sparql = reverse_replacements(encoded_sparql)
    sparql = reverse_shorten_query(short_sparql)
    return sparql


def reverse_replacements(sparql):
    for r in REPLACEMENTS:
        original = r[0]
        encoding = r[-1]
        sparql = sparql.replace(encoding, original)
        stripped_encoding = str.strip(encoding)
        sparql = sparql.replace(stripped_encoding, original)
    return sparql


def reverse_shorten_query(sparql):
    sparql = re.sub(r'_oba_ ([\S]+)', 'order by asc (\\1)', sparql,
                    flags=re.IGNORECASE)
    sparql = re.sub(r'_obd_ ([\S]+)', 'order by desc (\\1)', sparql,
                    flags=re.IGNORECASE)
    return sparql


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
