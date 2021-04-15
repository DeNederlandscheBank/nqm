#!/usr/bin/env python
"""
This script provides code to ask a question, translate it and return the
query.
"""

from fairseq.models.transformer import TransformerModel
from generator_utils import sparql_decode
from generator import query_database

def translate(question, model_data_dir):
    model = TransformerModel.from_pretrained(
      model_data_dir,
      checkpoint_file='./bot.pt',
      data_name_or_path=model_data_dir,
      bpe='subword_nmt',
      bpe_codes='./bot-bpe.codes',
      tokenizer = 'moses'
    )
    encoded_sparql = model.translate(question)
    decoded_sparql = sparql_decode(encoded_sparql)

    return decoded_sparql

def translate_and_query(question,model_data_dir, graph):
    sparql = translate(question, model_data_dir)

    results = query_database(sparql,graph)

    return results

if __name__ = '__main__':
