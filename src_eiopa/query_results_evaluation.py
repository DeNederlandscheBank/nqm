#!/usr/bin/env python
"""
This file reads in the output from decode_fairseq_output.py. This is a list
containing the true query and the generated query.
For every pair, the result is compared and in the end the accuracy is given.

Jan-Marc Glowienke, Intern at De Nederlandsche Bank 2021
"""

import argparse
import logging

from decode_fairseq_output import save_result
from generator import initialize_graph, query_database


def compare_results(graph, query_pairs):
    """
    Returns summary statistics for query results
    Also returns list of reference, translation and query results.
    If a query resulted in no answer, it is counted as false.
    """
    cnt_correct = 0
    cnt_false = 0
    queries_results = []
    for pair in query_pairs:
        try:
            results_reference = query_database(pair[0], graph)
        except Exception:
            logging.error(f'Error in Reference Query; {pair[0]}')
            continue
        try:
            results_generated = query_database(pair[1], graph)
        except Exception:
            logging.error(f'Error in Translated Query; {pair[1]}')
            cnt_false += 1
            continue
        if results_reference and results_generated:
            # value is not [], hence some result was found

            # the results are list of list, but we only have on result, hence
            # extracting first element of list
            results_reference = results_reference[0]
            results_generated = results_generated[0]
            for ref_result in results_reference:
                # check for each reference_result, whether present in results
                # of translation
                if ref_result in results_generated:
                    cnt_correct += 1
                else:
                    cnt_false += 1
                    logging.info(
                        f'Result Mismatch!; {pair[0]}; {pair[1]}; '
                        f'{results_reference}; {results_generated}')
            pair.append(results_reference)
            pair.append(results_generated)
            queries_results.append(pair)
        else:
            # if either the translation or reference returns an empty list
            # it is counted as false
            cnt_false += 1
            pair.append(results_reference)
            pair.append(results_generated)
            queries_results.append(pair)
            logging.info('Empty results!;' +
                         f'{pair[0]}; {pair[1]}; {results_reference};'
                         f' {results_generated}')
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
                # output files by fairseq-generate contain an ID code as
                # first element, which can be omitted
                _, reference, gen = line.strip('\n').split(",")
            query_list.append([reference, gen])
    src.close()
    return query_list


def save_query_results(file, result_list):
    with open(file, 'w', encoding='utf-8') as target:
        for line in result_list:
            for item in line[:-1]:
                target.writelines(str(item) + ', ')
            target.writelines(str(line[-1]) + '\n')
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
    logging.basicConfig(filename=log_file,
                        format='%(levelname)s - %(message)s',
                        level=logging.DEBUG)
    g = initialize_graph(args.graph_path)
    queries = read_queries(args.query_file, args.interactive_mode)
    acc, results = compare_results(g, queries)
    result_string = f'Query Result Accuracy: {acc[0]:.4f}, ' \
                    f'correct: {acc[1]}, false: {acc[2]}'
    save_query_results(args.out_file, results)
    if args.sum_file:
        save_result(result_string, args.query_file, args.sum_file)
    else:
        print(result_string)
