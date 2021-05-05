#!/usr/bin/env python
"""
This file reads in the output from decode_fairseq_output.py. This is a list
containing the true query and the generated query.
For every pair, the result is compared and in the end the accuracy is given.
"""

import argparse
import logging

from decode_fairseq_output import save_result
from generator import initialize_graph, query_database


def compare_results(graph, query_pairs):
    """
    Returns summary statistics for query results
    Also returns list of reference, translation and query results. If one
    of the queries resulted in no answer, the query is not written to
    the output file.
    """
    cnt_correct = 0
    cnt_false = 0
    queries_results = []
    for pair in query_pairs:
        try:
            result_true = query_database(pair[0], graph)
        except:
            logging.info(f'Error in Reference Query: {pair[0]}')
            continue
        try:
            result_generated = query_database(pair[1], graph)
        except:
            logging.info(f'Error in Translated Query: {pair[1]}')
            cnt_false += 1
            continue
        if result_true and result_generated:  # value is not []
            result_true = result_true[0]
            result_generated = result_generated[0]
            for index in range(len(result_true)):
                if result_true[index] == result_generated[index]:
                    cnt_correct += 1
                else:
                    cnt_false += 1
                    logging.debug(f'{pair[0]}, {pair[1]}')
                pair.append(result_true[index])
                pair.append(result_generated[index])
            queries_results.append(pair)
        else:
            cnt_false += 1
    if cnt_correct != 0 or cnt_false != 0:
        accuracy = cnt_correct / (cnt_correct + cnt_false)
    else:
        accuracy = 0

    return [accuracy, cnt_correct, cnt_false], queries_results


def read_queries(file, interactive=False):
    """ Return list of reference and generated queries """
    query_list = []
    with open(file, 'r') as src:
        for line in src.readlines():
            if interactive is True:
                reference, gen = line.strip('\n').split(",")
            else:
                _, reference, gen = line.strip('\n').split(",")
            query_list.append([reference, gen])
    src.close()
    return query_list


def save_query_results(file, result_list):
    with open(file, 'w', encoding='utf-8') as target:
        for line in result_list:
            for item in line:
                target.writelines(str(item) + ', ')
            target.writelines('\n')
    target.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--interactive', dest='interactive_mode',
                        action='store_true',
                        help='evaluate output from interactive mode')
    parser.add_argument('--query-file', dest='query_file',
                        help='true and generated queries', required=True)
    parser.add_argument('--graph-path', dest='graph_path',
                        help='path to graph data', required=True)
    parser.add_argument('--out-file', dest='out_file',
                        help='file to write outputs', required=True)
    parser.add_argument('--summary-file', dest='sum_file',
                        help='file to summarize evaluation results')
    args = parser.parse_args()

    log_file = f'{args.out_file[:-4]}.log'
    logging.basicConfig(filename=log_file, level=logging.DEBUG)
    g = initialize_graph(args.graph_path)
    queries = read_queries(args.query_file, args.interactive_mode)
    acc, results = compare_results(g, queries)
    result_string = f'Query Result Accuracy: {acc[0]}, correct: {acc[1]}, ' \
                    f'false: {acc[2]}'
    save_query_results(args.out_file, results)
    if args.sum_file:
        save_result(result_string, args.query_file, args.sum_file)
    else:
        print(result_string)
