def data2table(file, starred=True, write=True):
    tsv = ["ID\tTigrinya\tAmharic\tUD\tNotes"]
    with open(file, encoding='utf8') as file:
        current = []
        starred = False
        for line in file:
            if len(current) <= 2:
                if '*' in line:
                    starred = True
                    line = line.replace('*', '')
                current.append(line.strip())
            else:
                if starred:
                    tsv.append('\t'.join(current) + '\t \t ')
                starred = False
                if '*' in line:
                    starred = True
                    line = line.replace('*', '')
                current = [line.strip()]
    if write:
        with open("../data/ti_am_att-ud-test.tsv", 'w', encoding='utf8') as file:
            for line in tsv:
                print(line, file=file)
    return tsv
        
