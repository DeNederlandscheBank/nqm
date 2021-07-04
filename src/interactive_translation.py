#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Use this script from the root of the repo to interactively use
the various models tested for the research. Make sure to have the required
model files in the correct directory.
"""

import argparse
import glob
import os
import re
from os.path import join, split

from fairseq.models.transformer import TransformerModel
from sacremoses import MosesTokenizer

try:
    from src.generator import initialize_graph, query_database
    from src.generator_utils import sparql_decode
    from src.pg_postprocess import replace_oovs
    from src.pg_preprocess import replace_oov_input, remove_counts_vocabulary
except ImportError:
    # noinspection PyUnresolvedReferences
    from nqm.src.generator import initialize_graph, query_database
    from nqm.src.generator_utils import sparql_decode
    from nqm.src.pg_postprocess import replace_oovs
    from nqm.src.pg_preprocess import replace_oov_input, \
        remove_counts_vocabulary

GRAPH_DIR = join('data', 'eiopa', '1_external')

OPTIONS = {
    'a': 'ALPHA',
    'b': 'BRAVO',
    'c': 'CHARLIE',
    'c2': 'CHARLIE2',
    'd': 'DELTA',
    'd2': 'DELTA2',
    'e': 'ECHO',
    'f': 'FOXTROTT',
    'g': 'GOLF',
    'h': 'HOTEL',
    'i': 'INDIA',
    'j': 'JULIETT',
    'k': 'KILO',
    'l': 'LIMA'
}

MODELS = {
    'ALPHA': 'transformer',
    'BRAVO': 'transformer',
    'CHARLIE': 'align',
    'CHARLIE2': 'align',
    'DELTA': 'align',
    'DELTA2': 'align',
    'ECHO': 'subwords',
    'FOXTROTT': 'subwords',
    'GOLF': 'pointer_generator',
    'HOTEL': 'pointer_generator',
    'INDIA': 'subwords',
    'JULIETT': 'subwords',
    'KILO': None,
    'LIMA': 'xlmr'
}


def get_model_directory(model_option):
    """
    :return: path to model files
     """
    if split(os.getcwd())[1] == 'src':
        return join("..", "models", model_option, "")
    else:
        return join("models", model_option, "")


def get_checkpoint_file(path, checkpoint):
    """
    If checkpoint is not specified,
    this function finds the correct checkpoint file
     """
    if checkpoint is not None:
        return checkpoint
    else:
        file_list = glob.glob(path + "/*.pt")
        if not file_list:
            raise AssertionError("Please ensure a checkpoint file (.pt)"
                                 " is present")
        elif len(file_list) > 1:
            raise AssertionError(
                "Multiple checkpoint files present. Either ensure only 1 "
                "is present or indicate which checkpoint to use "
                "via --checkpoint")
        else:
            return split(file_list[0])[1]


def get_model(choice, checkpoint_choice=None):
    print("Model is loading...")
    option = OPTIONS.get(str.lower(choice))
    assert option is not None, "Recheck if you gave a valid value for '--model'"
    model_type = MODELS.get(option)
    model_path = get_model_directory(option)
    checkpoint = get_checkpoint_file(model_path, checkpoint_choice)

    if model_type == 'subwords':
        model = TransformerModel.from_pretrained(
            model_path,
            checkpoint_file=checkpoint,
            data_name_or_path=model_path,
            bpe='subword_nmt',
            bpe_codes=model_path + '/bpe.codes',
            tokenizer='moses',
            eval_bleu=False,
        )
    elif model_type == 'align':
        model = TransformerModel.from_pretrained(
            model_path,
            checkpoint_file=checkpoint,
            data_name_or_path=model_path,
            tokenizer='moses',
            eval_bleu=False,
            remove_unk=True
        )
    elif model_type == 'pointer_generator':
        model = TransformerModel.from_pretrained(
            model_path,
            checkpoint_file=checkpoint,
            data_name_or_path=model_path,
            eval_bleu=False
        )
        return model, model_path
    elif model_type == 'xlmr':
        model = TransformerModel.from_pretrained(
            model_path,
            checkpoint_file=checkpoint,
            data_name_or_path=model_path,
            eval_bleu=False,
            bpe='sentencepiece',
            sentencepiece_model='sentencepiece.bpe.xlmr.model',
            model_overrides={'pretrained_xlm_checkpoint': 'interactive'}
        )
    else:
        model = TransformerModel.from_pretrained(
            model_path,
            checkpoint_file=checkpoint,
            eval_bleu=False
        )
    print('Model loading finished!')
    return model, None


def translate(question, model, path):
    encoded_sparql = model.translate(question)
    decoded_sparql = sparql_decode(encoded_sparql)
    return decoded_sparql


def translate_and_query(question, model, graph, path):
    if path is not None:
        sparql = translate_pointer_generator(question, model, path)
    else:
        sparql = translate(question, model, path)
    results = query_database(sparql, graph)
    names = re.findall(r'"(.*?)"', sparql)
    name_string = ' and '.join(names)
    return results, sparql, name_string


def translate_pointer_generator(question, model, path):
    tokenizer = MosesTokenizer(lang='en')

    with open(path + '/dict.nl.txt', encoding="utf-8") as vocab:
        vocabulary_with_numbers = vocab.read().splitlines()
    vocab = remove_counts_vocabulary(vocabulary_with_numbers)

    question_preprocessed = replace_oov_input(question, vocab, tokenizer)
    encoded_sparql = model.translate(question_preprocessed)
    sparql_postprocessed = replace_oovs(encoded_sparql, question,
                                        interactive=True)[0]
    sparql = sparql_decode(sparql_postprocessed)
    return sparql


def main_translate(model_choice, checkpoint_choice):
    model, model_path = get_model(model_choice, checkpoint_choice)
    if model_path is not None:
        translate_function = translate_pointer_generator
    else:
        translate_function = translate
    try:
        while True:
            source_raw = input("\tUse Ctr+C to close the prompt\n"
                               "Enter the sequence to be translated:\n")
            translation = translate_function(source_raw, model, model_path)
            print(translation + "\n")
    except KeyboardInterrupt:
        print("\t Received Keyboard Interrupt\nFinishing the process")


def main_translate_query(model_choice, checkpoint_choice, graph):
    model, model_path = get_model(model_choice, checkpoint_choice)
    try:
        while True:
            source_raw = input("\tUse Ctr+C to close the prompt\n"
                               "Enter your question:\n")
            results, query, _ = translate_and_query(source_raw, model, graph,
                                                    model_path)
            if results:
                for result in results:
                    result_string = ', '.join(result)
            else:
                result_string = 'no result'
            print("Translation: " + query)
            print("Result: " + result_string + "\n")
    except KeyboardInterrupt:
        print("\t Received Keyboard Interrupt\nFinishing the process")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', dest='chosen_model',
                        help='choose model to use for translation',
                        required=True)
    parser.add_argument('--checkpoint', dest='checkpoint_choice',
                        help='indicate which checkpoint to use if multiple '
                             'present', required=False)
    parser.add_argument('--query-database', dest='choice_query',
                        action='store_true', required=False)
    args = parser.parse_args()
    if args.choice_query is True:
        if split(os.getcwd())[1] == 'src':
            GRAPH_DIR = join("..", GRAPH_DIR)
        graph_database = initialize_graph(GRAPH_DIR)
        main_translate_query(args.chosen_model, args.checkpoint_choice,
                             graph_database)
    else:
        main_translate(args.chosen_model, args.checkpoint_choice)
