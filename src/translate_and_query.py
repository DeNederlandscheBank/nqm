#!/usr/bin/env python
"""
This script provides code to ask a question, translate it and return the
query.
"""

import re

try:
    from src.generator import query_database
    from src.generator_utils import sparql_decode
    from src.pg_preprocess import replace_oov_input, \
        remove_counts_vocabulary
    from src.pg_postprocess import replace_oovs
    from sacremoses import MosesTokenizer
except ImportError:
    from nqm.src_eiopa.generator import query_database
    from nqm.src_eiopa.generator_utils import sparql_decode
    from nqm.src_eiopa.pg_preprocess import replace_oov_input
    from nqm.src_eiopa.pg_postprocess import replace_oovs


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


def translate_and_query_pointer_generator(question, model, graph,
                                          vocab, tokenizer):
    question_preprocessed = replace_oov_input(question, vocab, tokenizer)
    encoded_sparql = model.translate(question_preprocessed)
    sparql_postprocessed = replace_oovs(encoded_sparql, question, interactive = True)[0]
    sparql = sparql_decode(sparql_postprocessed)
    # results = query_database(sparql, graph)
    # names = re.findall(r'"(.*?)"', sparql)
    # name_string = ' and '.join(names)

    return 'results', sparql, 'name_string'


if __name__ == '__main__':
    from generator import initialize_graph
    from fairseq.models.transformer import TransformerModel
    model_data_dir = 'models/bot/pg_model'

    with open(model_data_dir + '/dict.nl.txt', encoding="utf-8") as vocab:
        vocabulary_with_numbers = vocab.read().splitlines()

    vocabulary = remove_counts_vocabulary(vocabulary_with_numbers)

    bot_model = TransformerModel.from_pretrained(
        model_data_dir,
        checkpoint_file='bot_pg.pt',
        data_name_or_path=model_data_dir,
        bpe='subword_nmt',
        bpe_codes=model_data_dir + '/bpe.codes',
        tokenizer='moses',
        eval_bleu=False,
        remove_unk = 'models/bot/alignment.nl-ql.txt'
    )
    
    moses_tokenizer = MosesTokenizer(lang='en')
    # g = initialize_graph('data/eiopa/1_external')
    # print(translate_and_query('Where is aegon?', bot_model, g))
    print(translate_and_query_pointer_generator('name achmea zorg verzekering n.v.',
                                                bot_model, 'g', vocabulary,
                                                moses_tokenizer))
