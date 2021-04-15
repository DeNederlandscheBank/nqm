#!/usr/bin/env python
"""
Split data set intro training and validation part.

Jan-Marc Glowienke
"""
import argparse
import random
import os
import io
from sklearn.model_selection import train_test_split


def split_datasets(query_file,nl_file,out_dir,train_split):
    """
    This function splits the natural language questions and queries into
    a train and validation part.
    It writes these to the given output directory
    """

    with io.open(query_file,encoding = 'utf-8') as query_org,\
            io.open(nl_file,encoding = 'utf8') as nl_org:
        ql = query_org.readlines()
        nl = nl_org.readlines()

        train_split = train_split / 100

        train_ql, val_ql, train_nl, val_nl = train_test_split(ql,nl,\
                                                train_size = train_split,\
                                                random_state = 42,\
                                                shuffle = True)

        with io.open(out_dir + "-train.ql", 'w', encoding = 'utf-8')\
                as ql_train,\
                io.open(out_dir + "-val.ql", 'w', encoding = 'utf-8')\
                    as ql_val,\
                io.open(out_dir + "-train.nl", 'w', encoding = 'utf-8')\
                    as nl_train,\
                io.open(out_dir + "-val.nl", 'w', encoding = 'utf-8')\
                    as nl_val:


            ql_train.writelines(train_ql)
            ql_val.writelines(val_ql)
            nl_train.writelines(train_nl)
            nl_val.writelines(val_nl)

    return True


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
                                metavar = 'train_test_split',
                                help='part to be in train set',required = True)
    args = parser.parse_args()

    dataset_file = os.path.splitext(args.dataset)[0]
    query_file = dataset_file + '-train_val' + ".ql"
    nl_file = dataset_file + '-train_val' + ".nl"
    train_split = int(args.split)
    outdir = os.path.splitext(args.outdir)[0]


    split_datasets(query_file,nl_file,outdir,train_split)

    print("Splitting sucessfull!")
