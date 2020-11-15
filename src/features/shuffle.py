import random
for file in ['../../data/interim/train_en.txt']:
    with open(file,'r', encoding='utf-8') as source:
        data = [line for line in source]

    with open('../../data/interim/train_sparql.txt','r',encoding='utf-8') as target:
        data_tgt = [line for line in target]

    c = list(zip(data, data_tgt))

    random.shuffle(c)

    data, data_tgt = zip(*c)

    with open('../../data/interim/train_sparql_shuf.txt','w',encoding='utf-8') as target:
        for line in data_tgt:
            target.write( line )
    with open(file[:-4] +'_shuff.txt','w',encoding='utf-8') as target:
        for line in data:
            target.write( line )
