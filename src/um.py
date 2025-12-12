### Process list from UM repository, dropping non-verbs and non-finite verbs

EXCLUDE = {'N', 'ADJ', 'NFIN', 'V.CVB', 'V.MSDR'}

def filter(write=True):
    lines = []
    with open("../../../../Projects/UM/amh/amh") as file:
        for line in file:
            root, form, feats = line.split()
            feats = feats.split(';')
            if EXCLUDE.intersection(feats):
                continue
            feats.remove('V')
            feats = ';'.join(feats)
            lines.append("{}\t{}\t{}".format(form, root, feats))
    if write:
        with open("../text/am/um.txt", 'w') as file:
            for line in lines:
                print(line, file=file)
    else:
        return lines
