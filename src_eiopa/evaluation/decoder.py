#!/usr/bin/env python
"""

Neural SPARQL Machines - Generator utils.

'SPARQL as a Foreign Language' by Tommaso Soru and Edgard Marx et al.,
 SEMANTiCS 2017
https://arxiv.org/abs/1708.07624

Version 1.0.0

Adapted for DNB NQM, large parts stripped

"""
import re


def strip_brackets(s):
    s = re.sub(r'\([^)]*\)', '', s)
    if "," in s:
        s = s[:s.index(",")]
    return s.strip().lower()


REPLACEMENTS = [
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
    [' > ', ' math_gt ']
]


def decode(encoded_sparql):
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
