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
from os.path import join, split

from fairseq.models.transformer import TransformerModel

from src.generator_utils import sparql_decode

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
    return model


def translate(question, model):
    encoded_sparql = model.translate(question)
    decoded_sparql = sparql_decode(encoded_sparql)
    return decoded_sparql


def main(model_choice, checkpoint_choice, query_choice):
    model = get_model(model_choice, checkpoint_choice)
    try:
        while True:
            source_raw = input("\tUse Ctr+C to close the prompt\n"
                               "Enter the sequence to be translated:\n")
            translation = translate(source_raw,model)
            print(translation + "\n")
    except KeyboardInterrupt:
        print("\t Receveived Keyboard Interrupt\nFinishing the process")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', dest='chosen_model',
                        help='choose model to use for translation',
                        required=True)
    parser.add_argument('--checkpoint', dest='checkpoint_choice',
                        help='indicate which checkpoint to use if multiple '
                             'present', required=False)
    parser.add_argument('--query', dest='choice_query',
                        action='store_true', required=False)
    args = parser.parse_args()
    main(args.chosen_model, args.checkpoint_choice, args.choice_query)
