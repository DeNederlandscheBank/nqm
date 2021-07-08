#!/usr/bin/env python3
"""
This file contains code to postprocess output of a pointer-generator
translation model, where <unk-N> need to be replaced.

Modified by Jan-Marc Glowienke and taken from:
https://github.com/pytorch/fairseq/blob/master/examples/pointer_generator/postprocess.py
Copyright (c) Facebook, Inc. and its affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

import re
import argparse
import sys

class OOVIndexError(IndexError):
    def __init__(self, pos, source_seq, target_seq):
        super(OOVIndexError, self).__init__(
            "A <unk-N> tag in the target sequence refers to a position that is "
            "outside the source sequence. Most likely there was a mismatch in "
            "provided source and target sequences. Otherwise this would mean that "
            "the pointing mechanism somehow attended to a position that is past "
            "the actual sequence end."
        )
        self.source_pos = pos
        self.source_seq = source_seq
        self.target_seq = target_seq


def replace_oovs(target_in, source_file_in, interactive=False):
    """ Adapted for interactive use
    Replaces <unk-N> tokens in the target text with the corresponding word in
    the source text.

    """
    oov_re = re.compile("^<unk-([0-9]+)>$")

    if interactive is False:
        source_in = []
        with open(source_file_in, 'r', encoding='utf-8') as src:
            for line in src.readlines():
                source_in.append(line.strip('\n'))
        src.close()
    else:
        # in interactive mode, variables below are given as string
        # should be in list format
        source_in = [source_file_in]
        target_in = [target_in]

    target_out = []
    try:
        for source_seq, target_seq in zip(source_in, target_in):
            target_seq_out = []

            pos_to_word = source_seq.strip().split()
            for token in target_seq.strip().split():
                m = oov_re.match(token)
                if m:
                    pos = int(m.group(1))
                    if pos >= len(pos_to_word):
                        raise OOVIndexError(pos, source_seq, target_seq)
                    token_out = pos_to_word[pos]
                else:
                    token_out = token
                target_seq_out.append(token_out)
            target_out.append(" ".join(target_seq_out))
    except OOVIndexError as e:
        print(e, file=sys.stderr)
        print("Source sequence:", e.source_seq.strip(), file=sys.stderr)
        print("Target sequence:", e.target_seq.strip(), file=sys.stderr)
        print(
            "Source sequence length:",
            len(e.source_seq.strip().split()),
            file=sys.stderr,
        )
        print("The offending tag points to:", e.source_pos)
        sys.exit(2)
    return target_out


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--in-file', dest='input_file',
                        help='generated translations', required=True)
    parser.add_argument('--in-file-reference', dest='reference_file',
                        help='reference translations', required=False)
    args = parser.parse_args()

    target = []
    with open(args.input_file, 'r', encoding='utf-8') as src:
        for line in src.readlines():
            target.append(line.strip('\n'))
    src.close()

    results_list = replace_oovs(target, args.reference_file)

    print(results_list)
