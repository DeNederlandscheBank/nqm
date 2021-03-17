#!/usr/bin/env python
"""

This script contains some utils to be used when running NLP models
using PyTorch and torchtext for Neural Machine Translation

Jan-Marc Glowienke

"""

import torchtext
import torch
from torchtext.data.utils import get_tokenizer
from collections import Counter
from torchtext.vocab import Vocab
# from torchtext.utils import download_from_url, extract_archive
import io
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

EN_TOKENIZER = get_tokenizer('spacy', language='en_core_web_sm')
QL_TOKENIZER = get_tokenizer('spacy', language='en_core_web_sm')
BATCH_SIZE = 128
PAD_IDX = de_vocab['<pad>']
BOS_IDX = de_vocab['<bos>']
EOS_IDX = de_vocab['<eos>']



def build_vocab(filepath, tokenizer):
    ''' Build a vocabulary from the input file '''
    counter = Counter()
    with io.open(filepath, encoding="utf8") as f:
        for string_ in f:
            counter.update(tokenizer(string_))
    return Vocab(counter, specials=['<unk>', '<pad>', '<bos>', '<eos>'])

def data_process(vocab_nl, vocab_ql,path_nl,path_ql,
                nl_tokenizer = EN_TOKENIZER, ql_tokenizer = QL_TOKENIZER):
    '''
    Returns a dataset with tuple elements containing tensors for the natural
    language and query language. The data is processed using the input
    tokenizer and vocabulary.
    '''
    raw_nl_iter = iter(io.open(path_nl, encoding="utf8"))
    raw_ql_iter = iter(io.open(path_ql, encoding="utf8"))
    data = []
    for (raw_nl, raw_ql) in zip(raw_nl_iter, raw_ql_iter):
        nl_tensor_ = torch.tensor(
            [vocab_nl[token] for token in nl_tokenizer(raw_nl)],
            dtype=torch.long
                                )
        ql_tensor_ = torch.tensor(
            [vocab_ql[token] for token in ql_tokenizer(raw_ql)],
            dtype=torch.long
                                )
        data.append((nl_tensor_, ql_tensor_))
    return data


def generate_batch(data_batch):
    '''
    Add BOS and EOS index to sentences. All sequences in the batch are
    padded to equal length.
    '''
    nl_batch, ql_batch = [], []
    for (nl_item, ql_item) in data_batch:
        nl_batch.append(torch.cat([torch.tensor([BOS_IDX]), nl_item,
                        torch.tensor([EOS_IDX])], dim=0)
                        )
        ql_batch.append(torch.cat([torch.tensor([BOS_IDX]), ql_item,
                                torch.tensor([EOS_IDX])], dim=0)
                                )
    nl_batch = pad_sequence(nl_batch, padding_value=PAD_IDX)
    ql_batch = pad_sequence(ql_batch, padding_value=PAD_IDX)
    return de_batch, en_batch

def create_data_loader(vocab_nl,vocab_ql,):
    '''
    Return a fully fucntional dataloader
    '''










if __name__ == "__main__":
    print("Executing utils")
