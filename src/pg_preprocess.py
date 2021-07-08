#!/usr/bin/env python3
"""
This file contains code to preprocess input of a pointer-generator
translation model, where <unk-N> need to be placed.

Modified by Jan-Marc Glowienke and taken from:
https://github.com/pytorch/fairseq/blob/master/examples/pointer_generator/preprocess.py
Copyright (c) Facebook, Inc. and its affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

import argparse
from itertools import zip_longest
from sacremoses import MosesTokenizer


def replace_oovs(source_in, target_in, vocabulary, source_out, target_out):
    """Replaces out-of-vocabulary words in source and target text with <unk-N>,
    where N in is the position of the word in the source sequence.
    """

    def format_unk(pos):
        return "<unk-{}>".format(pos)

    if target_in is None:
        target_in = []

    for seq_num, (source_seq, target_seq) in enumerate(
            zip_longest(source_in, target_in)
    ):
        source_seq_out = []
        target_seq_out = []

        word_to_pos = dict()
        for position, token in enumerate(source_seq.strip().split()):
            if token in vocabulary:
                token_out = token
            else:
                if token in word_to_pos:
                    oov_pos = word_to_pos[token]
                else:
                    word_to_pos[token] = position
                    oov_pos = position
                token_out = format_unk(oov_pos)
            source_seq_out.append(token_out)
        source_out.write(" ".join(source_seq_out) + "\n")

        if target_seq is not None:
            for token in target_seq.strip().split():
                if token in word_to_pos:
                    token_out = format_unk(word_to_pos[token])
                else:
                    token_out = token
                target_seq_out.append(token_out)
        if target_out is not None:
            target_out.write(" ".join(target_seq_out) + "\n")


def replace_oov_input(source, vocabulary, tokenizer):
    """  Marc Glowienke
    replace OOV words by <unk-N> inplace in input sequence
    can be used for interactive translation
    """

    def format_unk(pos):
        return "<unk-{}>".format(pos)

    source_tokens = tokenizer.tokenize(source.strip())
    source_tokens_out = []

    word_to_pos = dict()
    for position, token in enumerate(source_tokens):
        if token in vocabulary:
            token_out = token
        else:
            if token in word_to_pos:
                oov_pos = word_to_pos[token]
            else:
                word_to_pos[token] = position
                oov_pos = position
            token_out = format_unk(oov_pos)
        source_tokens_out.append(token_out)
    return ' '.join(source_tokens_out)


def remove_counts_vocabulary(vocab)
    """ Marc Glowienke, return vocabulary without counts """
    vocabulary = []
    for item in vocab:
        if len(item.split(" ")) > 1:
            # only split if dict contains words and counts
            item = item.split(" ")[0].strip(" ")
        vocabulary.append(item)
    return vocabulary


def main():
    parser = argparse.ArgumentParser(
        description="Replaces out-of-vocabulary words in both source and target "
                    "sequences with tokens that indicate the position of the word "
                    "in the source sequence."
    )
    parser.add_argument(
        "--source", type=str, help="text file with source sequences",
        required=True
    )
    parser.add_argument(
        "--target", type=str, help="text file with target sequences",
        default=None
    )
    parser.add_argument("--vocab", type=str, help="vocabulary file",
                        required=True)
    parser.add_argument("--source-out", type=str,
                        help="where to write source sequences with <unk-N> entries",
                        required=True,
                        )
    parser.add_argument(
        "--target-out",
        type=str,
        help="where to write target sequences with <unk-N> entries",
        default=None,
    )
    args = parser.parse_args()

    with open(args.vocab, encoding="utf-8") as vocab:
        vocabulary_with_numbers = vocab.read().splitlines()

    vocabulary = remove_counts_vocabulary(vocabulary_with_numbers)

    target_in = (
        open(args.target, "r",
             encoding="utf-8") if args.target is not None else None
    )
    target_out = (
        open(args.target_out, "w", encoding="utf-8")
        if args.target_out is not None
        else None
    )
    with open(args.source, "r", encoding="utf-8") as source_in, open(
            args.source_out, "w", encoding="utf-8"
    ) as source_out:
        replace_oovs(source_in, target_in, vocabulary, source_out, target_out)
    if target_in is not None:
        target_in.close()
    if target_out is not None:
        target_out.close()


def main_replace_oov_inplace():
    vocab_file = 'data/eiopa/5_model_input/fairseq-data-bin-15285/dict.nl.txt'

    with open(vocab_file, encoding="utf-8") as vocab:
        vocabulary_with_numbers = vocab.read().splitlines()

    vocabulary = remove_counts_vocabulary(vocabulary_with_numbers)

    moses_tokenizer = MosesTokenizer(lang='en')
    print(replace_oov_input("register name of achmea zorg?", vocabulary,
                            moses_tokenizer))


if __name__ == "__main__":
    main()
    # main_replace_oov_inplace()
