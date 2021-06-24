#!/usr/bin/env python
"""

Functions for pre- and postprocessing for using subwords with
the sentencepiece python wrapper

Jan-Marc Glowienke

"""

import sentencepiece as spm
import argparse


def preprocess_file(input_file, output_file, model):
    """ Preprocess a file using a sentencepiece model"""
    items_processed = []
    items = read_file(input_file)
    sp = spm.SentencePieceProcessor(model_file=model)
    items_processed_raw = sp.encode(items, out_type=str)
    # encode returns list of list, merge into single list of strings
    for item in items_processed_raw:
        tmp = ' '.join(item)
        items_processed.append(tmp)
    write_file(items_processed, output_file)


def train_model(input_file, model_name, vocab_size):
    """ Train a new sentencepiece model """
    spm.SentencePieceTrainer.train(
        f'--input={input_file} --model_prefix={model_name}'
        f' --model_type=bpe --vocab_size=500')


def read_file(file_directory):
    """ """
    text = []
    with open(file_directory, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            text.append(line.strip('\n'))
    file.close()
    return text


def write_file(text, output_directory):
    """ """
    with open(output_directory, 'w', encoding='utf-8') as target:
        for item in text:
            target.writelines(item + '\n')
    target.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--in-file', dest='input_file',
                        help='file with queries/questions to be processed',
                        required=True)
    parser.add_argument('--out-file', dest='output_file',
                        help='directory for output file',
                        required=False)
    parser.add_argument('--preprocess-file', dest='preprocess_file',
                        help='use this flag when file should be preprocessed',
                        required=False, action='store_true')
    parser.add_argument('--train_model', dest='train',
                        help='use this flag when a new model should be trained',
                        required=False, action='store_true')
    parser.add_argument('--model', dest='model_file',
                        help='model for sentencepiece processing')
    args = parser.parse_args()

    if args.preprocess_file is True:
        assert isinstance(args.out_file, object), "When preprocessing define " \
                                                  "'--out-file "
        preprocess_file(args.input_file, args.output_file, args.model_file)

    if args.train is True:
        train_model(args.input_file, args.model_file, 10)
