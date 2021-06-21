#!/usr/bin/env python
"""
Split data set intro training and validation part.

Jan-Marc Glowienke, Intern at De Nederlandsche Bank 2021
"""
import argparse
import io
import os

from sklearn.model_selection import train_test_split


def split_datasets(ql_file, nl_question_file, output_dir, split):
    """
    This function splits the natural language questions and queries into
    a train and validation part.
    It writes these to the given output directory
    """

    with io.open(ql_file, encoding='utf-8') as query_org, \
            io.open(nl_question_file, encoding='utf8') as nl_org:
        ql = query_org.readlines()
        nl = nl_org.readlines()

        split = split / 100

        train_ql, val_ql, train_nl, val_nl = train_test_split(ql, nl,
                                                              train_size=split,
                                                              random_state=42,
                                                              shuffle=True)

        with io.open(output_dir + "-train.ql", 'w', encoding='utf-8') \
                as ql_train, \
                io.open(output_dir + "-val.ql", 'w', encoding='utf-8') \
                as ql_val, \
                io.open(output_dir + "-train.nl", 'w', encoding='utf-8') \
                as nl_train, \
                io.open(output_dir + "-val.nl", 'w', encoding='utf-8') \
                as nl_val:
            ql_train.writelines(train_ql)
            ql_val.writelines(val_ql)
            nl_train.writelines(train_nl)
            nl_val.writelines(val_nl)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('--inputPath', dest='dataset',
                               metavar='dataset.sparql',
                               help='sparql dataset file', required=True)
    requiredNamed.add_argument('--outputPath', dest='outdir',
                               metavar='outputdirectory',
                               help='directory where output is written',
                               required=True)
    requiredNamed.add_argument('--split', dest='split',
                               metavar='train_test_split',
                               help='part to be in train set', required=True)
    args = parser.parse_args()

    dataset_file = os.path.splitext(args.dataset)[0]
    query_file = dataset_file + '-train_val' + ".ql"
    nl_file = dataset_file + '-train_val' + ".nl"
    out_dir = os.path.splitext(args.outdir)[0]
    train_split = int(args.split)
    try:
        assert 1 < train_split <= 100
    except AssertionError:
        raise Exception('Value for "--split" needs to be given as percentage,'
                        'so it should be a value between 0 and 100, e.g. 80.')

    split_datasets(query_file, nl_file, out_dir, train_split)

    print("Splitting successfully!")
