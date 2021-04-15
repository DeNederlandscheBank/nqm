#!/usr/bin/env python
"""
This file reads in the output from decode_fairseq_output.py. This is a list
containing the true query and the generated query.
For every pair, the result is compared and in the end the accuracy is given.
"""

import argparse

from generator import initialize_graph, query_database


def compare_results(graph, query_pairs):
    """ Returns summary statistics for query results """
    cnt_correct = 0
    cnt_false = 0
    queries_results = []
    for pair in query_pairs:
        result_true = query_database(pair[0], graph)
        result_generated = query_database(pair[1], graph)
        if result_true and result_generated:  # value is not []
            result_true = result_true[0]
            result_generated = result_generated[0]
            for index in range(len(result_true)):
                if result_true[index] == result_generated[index]:
                    cnt_correct += 1
                else:
                    cnt_false += 1
                pair.append(result_true[index])
                pair.append(result_generated[index])
            queries_results.append(pair)
        else:
            cnt_false += 1
    accuracy = cnt_correct / (cnt_correct + cnt_false)

    return accuracy, queries_results


def read_queries(file):
    """ Return list of true and generated queries """
    query_list = []
    with open(file, 'r') as src:
        for line in src.readlines():
            _, true, gen, _ = line.split(",")
            query_list.append([true, gen])
    src.close()
    return query_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--query-file', dest='query_file',
                        help='true and generated queries', required=True)
    parser.add_argument('--graph-path', dest='graph_path',
                        help='path to graph data', required=True)
    parser.add_argument('--out-file', dest='out_file',
                        help='file to write outputs', required=True)
    args = parser.parse_args()

    g = initialize_graph(args.graph_path)
    queries = read_queries(args.query_file)
    acc, results = compare_results(g, queries)

    with open(args.out_file, 'w', encoding='utf-8') as target:
        for line in results:
            for item in line:
                target.writelines(str(item) + ', ')
            target.writelines('\n')
        target.writelines(str(acc))
        target.close()
