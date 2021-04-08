from decoder import decode,fix_URI


file = '../../data/nqm/processed/test_sparql_model.txt'
with open(file,'r', encoding='utf-8') as source:
    data = [line for line in source]

with open('../../data/nqm/processed/test_decoded.txt','w',encoding='utf-8') as target:
    for line in data:
        line = decode(line)
        line = fix_URI(line)
        target.write( line )
