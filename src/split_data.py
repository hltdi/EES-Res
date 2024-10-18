'''
Merging and splitting data files.
'''
import random

def ti_update_data(datafile, write=None):
    lines = []
    include = False
    group = []
    position = 0
    with open(datafile, encoding='utf8') as file:
        for line in file:
            line = line.strip()
            if line[0] == '#':
                if group:
                    # include the last group
                    lines.extend(group)
                group = [line]
                position = 0
            elif position == 0:
                if '/' in line or '--' in line:
                    group.append(line)
                    include = True
                else:
                    group = []
                    include = False
                position += 1
            elif include:
                group.append(line)
    return lines

def filter_data(datafile, ids, write=None):
    lines = []
    include = False
    with open(datafile, encoding='utf8') as file:
        for line in file:
            line = line.strip()
            if line[0] == '#':
                if line in ids:
                    include = True
                    lines.append(line)
                else:
                    include = False
            elif include:
                lines.append(line)
    if write:
        with open(write, 'w', encoding='utf8') as file:
            for line in lines:
                print(line, file=file)
    else:
        return lines

def get_split_ids(file):
    ids = []
    with open(file, encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if line[0] == '#':
                ids.append(line)
    return ids

def add_am(file, am_data):
    lines = []
    id = ''
    a = ''
    with open(file, encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if line[0] == '#':
                id = line
                id0 = id.replace("sent_id = ", "data_UD-")
                a = am_data[id0]
            else:
                lines.extend([id, line, a])
                id = ''
                a = ''
    return lines

def am_data_dict( am_data):
    am = {}
    id = ''
    with open(am_data, encoding='utf8') as file:
        for line in file:
            line = line.strip()
            if line[0] == '#':
                id = line
            else:
                am[id] = line
                id = ''
    return am

def combine_tiam(file1, file2, dups):
    lines = []
    elim = False
    with open(file1, encoding='utf8') as file:
        for line in file:
            line = line.strip()
            if line[0] == '#':
                if line in dups:
                    elim = True
                else:
                    elim = False
                    lines.append(line)
            elif elim:
                continue
            else:
                lines.append(line)
    with open(file2, encoding='utf8') as file:
        for line in file:
            line = line.strip()
            if line[0] == '#':
                if line in dups:
                    elim = True
                else:
                    elim = False
                    lines.append(line)
            elif elim:
                continue
            else:
                lines.append(line)
    return lines

def reduce_dups(dupfile):
    lines = []
    with open(dupfile, encoding='utf8') as file:
        position = 0
        sentences = []
        ids = []
        for line in file:
            line = line.strip()
            if not line:
                # end of a group, add to lines
                id = ids[0] if len(ids[0]) < len(ids[1]) else ids[1]
                if sentences[0] == sentences[1]:
                    s = sentences[0]
                else:
                    s = ' / '.join(sentences)
                lines.append((id, s))
                position = 0
                sentences = []
                ids = []
                continue
            if line[0] == '#':
                ids.append(line)
                position += 1
            else:
                sentences.append(line)
                position += 1
    return lines

def get_ti(inpath, ti_index=0):
    '''
    Returns the ids and sentences for items in inpath with Ti translations.
    '''
    ti = []
    id = ''
    sentence = ''
    ids = []
    position = 0
    with open(inpath, encoding='utf8') as file:
        for line in file:
            line = line.strip()
            if line[0] == '#':
                id = line
                if id in ids:
                    print("Duplicate: {}".format(id))
                ids.append(id)
                position = 0
            elif position == ti_index:
                if line == '--':
                    continue
                sentence = line
                ti.append((id, line))
                position += 1
            else:
                if line == sentence:
                    print("Ti is Am: {}".format(line))
    return ti

def find_dups(inpath1, write1, pos=0):
    dups = []
    sentences = {}
    group = []
    lines = []
    id = ''
    ids = {}
    position = 0
    dup = False
    with open(inpath1, encoding='utf8') as f1:
        for line in f1:
            line = line.strip()
            if line[0] == '#':
                position = 0
                id = line.replace("data_UD-", "sent_id = ")
                if not dup:
                    lines.extend(group)
                dup = False
                group = [line]
            elif position == pos:
                if line in sentences:
                    print("Dup 1: {}".format(line))
                    dups.append(line)
                    ids[id] = sentences[line]
                    ids[sentences[line]] = id
                    dup = True
                else:
                    sentences[line] = id
                    group.append(line)
                position += 1
            else:
                group.append(line)
                position += 1
    if not dup:
        lines.extend(group)
    if write1:
        with open(write1, 'w', encoding='utf8') as f1:
            for line in lines:
                print(line, file=f1)
    return dups, ids
##    position = 0
##    with open(inpath2, encoding='utf8') as f2:
##        for line in f2:
##            line = line.strip()
##            if line[0] == '#':
##                position = 0
##            elif position == 1:
##                if line in sentences:
##                    print("Dup 2: {}".format(line))
##                    dups.append(line)
##                else:
##                    sentences.append(line)
##                position += 1
##            else:
##                position += 1    
##    return dups

def sep_lang(inpath, outpath, langid=1):
    '''
    Create a new data file with just the sentences in langid position.
    '''
    lines = []
    position = 0
    with open(inpath, encoding='utf8') as infile:
        for line in infile:
            line = line.strip()
            if line[0] == '#':
                position = 0
                lines.append(line)
            elif position == langid:
                lines.append(line)
                position += 1
            else:
                position += 1
    with open(outpath, 'w', encoding='utf8') as outfile:
        for line in lines:
            print(line, file=outfile)

def triples(path, scramble=False):
    data = []
    with open(path, encoding='utf8') as file:
        lines = file.read().split("\n")
        n = len(lines)
        for i in range(0, n, 3):
            id = lines[i].partition('-')[-1]
            id = "# sent_id = {}".format(id)
            tsent = lines[i+1]
            tsent = tsent.rpartition("#")[0].strip() or tsent
            asent = lines[i+2]
            data.append((id, tsent, asent))
    if scramble:
        random.shuffle(data)
    return data

def split(data, path1, path2):
    n = len(data)
    n2 = n // 2
    with open(path1, 'w', encoding='utf8') as file:
        for i in range(n2):
            d = data[i]
            print(d[0], file=file)
            print(d[1], file=file)
            print(d[2], file=file)
    with open(path2, 'w', encoding='utf8') as file:
        for i in range(n2, n):
             d = data[i]
             print(d[0], file=file)
             print(d[1], file=file)
             print(d[2], file=file)
           
            

            


            

        
