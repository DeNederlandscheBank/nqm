#!/usr/bin/env python
"""
This script provides code to ask a question, translate it and return the
query.
"""

import re

try:
    from src_eiopa.generator import query_database
    from src_eiopa.generator_utils import sparql_decode
except:
    from nqm.src_eiopa.generator import query_database
    from nqm.src_eiopa.generator_utils import sparql_decode


def translate(question, model):
    encoded_sparql = model.translate(question)
    decoded_sparql = sparql_decode(encoded_sparql)
    return decoded_sparql


def translate_and_query(question, model, graph):
    sparql = translate(question, model)
    results = query_database(sparql, graph)
    names = re.findall(r'"(.*?)"', sparql)
    name_string = ' and '.join(names)
    return results, sparql, name_string


if __name__ == '__main__':
    from generator import initialize_graph
    from fairseq.models.transformer import TransformerModel
    model_data_dir = 'models/bot'

    bot_model = TransformerModel.from_pretrained(
        model_data_dir,
        checkpoint_file='bot.pt',
        data_name_or_path=model_data_dir,
        bpe='subword_nmt',
        bpe_codes=model_data_dir + '/bpe.codes',
        tokenizer='moses',
        eval_bleu=False
    )

    g = initialize_graph('data/eiopa/1_external')
    print(translate_and_query('Where is aegon?', bot_model, g))
