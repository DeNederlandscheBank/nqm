from generator_utils import decode,fix_URI


file = '../../data/interim/test_spar.txt'
with open(file,'r', encoding='utf-8') as source:
    data = [line for line in source]

with open('../../data/interim/test_decoded.txt','w',encoding='utf-8') as target:
    for line in data:
        line = decode(line)
        line = fix_URI(line)
        target.write( line )
