#!/usr/bin/env python
"""
 NQM - Jan-Marc Glowienke

 Read in generated fairseq data and output file with true and generated queries
"""
import argparse

from generator_utils import sparql_decode


def read_in_generated_data(in_file):
    results = []
    with open(in_file, 'r') as f:
        for line in f.readlines():
            if line.startswith('T') is True:
                head, sentence = line.split('\t')
                # only take index number and sentence,
                # delete \n from end of sentence
                tmp = [int(head.split('-')[1]), sparql_decode(sentence[:-1])]
            elif line.startswith('D') is True:
                head, score, sentence = line.split('\t')
                if int(head.split('-')[1]) == tmp[0]:
                    tmp.append(sparql_decode(sentence[:-1]))
                    results.append(tmp)
                    del tmp
                else:
                    raise ValueError(
                        "Mismatch in available true and translated "
                        "sentences! \n Please check that for every "
                        "true sentence (T) there is an translation "
                        "available (D) in the generated file! Error "
                        "ocurred for translation {}".format(head))
            elif line.startswith('Generate') is True:
                result = line[:-1]
                print('Result:', result)
    f.close()
    return results, result


def write_queries(results, out_file):
    with open(out_file, 'w', encoding='utf-8') as target:
        for line in results:
            for item in line:
                target.writelines(str(item) + ', ')
            target.writelines('\n')
    target.close()


def save_result(item, file, summary_file):
    with open(summary_file, 'w', encoding='utf-8') as tgt:
        tgt.writelines(file.split("/")[-1] + ':\n')
        tgt.writelines(item)
        tgt.writelines('\n')
    tgt.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--in-file', dest='input_file',
                        help='generated translations', required=True)
    parser.add_argument('--out-file', dest='output_file',
                        help='file directory to write output', required=True)
    parser.add_argument('--summary-file', dest='sum_file',
                        help='file to summarize evaluation results')
    args = parser.parse_args()

    results_list, result = read_in_generated_data(args.input_file)
    write_queries(results_list, args.output_file)

    if args.sum_file:
        save_result(result, args.output_file, args.sum_file)
