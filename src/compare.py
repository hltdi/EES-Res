'''
Comparing treebanks.
Merging and splitting data files.
Finding duplicates
'''

from conllu import parse, TokenList, Token
import os, re, random

DIR = "../treebanks/"

USERS = ['megasser', 'abutihere', 'nazarethamlesom']

ID_RE = re.compile(r'(\d+)([a-zA-Z]*)')

def read_text(path="../text/amti/am_ti_starter.txt"):
    '''
    Read in a text file consisting of triples of lines (comment, Amh, Tir)
    and return it as a dict.
    '''
    group = []
    groups = {}
    comment = ''
    amh = []
    with open(path, encoding='utf8') as old:
        for line in old:
            line = line.strip()
            if line[0] == '#':
                if group:
                    groups[comment] = group
                comment = line
                group = []
            else:
                group.append(line)
        if group:
            groups[comment] = group
    return groups

def rewrite():
    group = []
    lines = {}
    comment = ''
    amh = []
    with open("../text/amti/ti_am_att-ud.txt", encoding='utf8') as old:
        for line in old:
            line = line.strip()
            if line[0] == '#':
                if group:
                    lines[comment] = group
                comment = line
                group = []
            else:
                group.append(line)
        if group:
            lines[comment] = group
    with open("../text/amti/am_ti_att-ud.txt", 'w', encoding='utf8') as new:
        for id, (t, a) in lines.items():
            if a in amh:
                print("{} is repeated".format(id))
            else:
                amh.append(a)
                print(id, file=new)
                print(a, file=new)
                print(t, file=new)

def reorder():
    group = []
    ids = []
    comment = ''
    lines = {}
    with open("../text/am/am_att-ud-test.txt", encoding='utf8') as att:
        for line in att:
            line = line.strip()
            if line[0] == '#':
                line = line.replace('data_UD-', 'sent_id = ')
                ids.append(line)
    with open("../text/amti/am_ti_starter.txt", encoding='utf8') as new:
        for line in new:
            line = line.strip()
            if line[0] == '#':
                if group:
                    lines[comment] = group
                comment = line
                group = []
            else:
                group.append(line)
        if group:
            lines[comment] = group
    for id in ids:
        group = lines.get(id)
        if not group:
            print("{} not found".format(id))

def merge_ti(original, new):
    group = []
    comment = ''
    lines = {}
    newlines = {}
    with open(original, encoding='utf8') as file:
        for line in file:
            line = line.strip()
            if line[0] == '#':
                if group:
                    lines[comment] = group
                comment = line
                group = []
            else:
                group.append(line)
        if group:
            lines[comment] = group
    group = []
    comment = ''
    position = 0
    with open(new, encoding='utf8') as file:
        for line in file:
            line = line.strip()
            if line[0] == '#':
                if line not in lines:
                    print("{} missing from original".format(line))
                else:
                    comment = line
                    group = lines[comment]
                    position = 0
            elif position == 0:
                # line is new Ti
                # old Ti
                oldti = group[0]
                if oldti != line:
                    # Correcting new Ti
                    if line[-2] != ' ':
                        line = line[:-1] + ' ' + line[-1]
                        line.replace(" አ", " ኣ")
                        if line[0] == 'አ':
                            line = 'ኣ' + line[1:]
                    print("Replacing {} with {}".format(oldti, line))
                    group[0] = line
                position += 1
        
    return lines

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
           
def language_dir(language, user):
    if language in ('t', 'ti'):
        language = 'tir'
    elif language in ('a', 'am'):
        language = 'amh'
    if user in ('abu', 'a'):
        user = 'abutihere'
    if user in ('naz', 'n'):
        user = 'nazarethamlesom'
    if user in ('mg', 'm'):
        user = 'megasser'
    return os.path.join(DIR, language, 'syntax', user)

def get_data(language, user1, user2, filename):
    '''
    language is "tir"/"ti"/"t" or "amh"/"am"/"a"
    '''
    directory1 = language_dir(language, user1)
    directory2 = language_dir(language, user2)
    file1 = open(os.path.join(directory1, filename), 'r', encoding='utf8')
    file2 = open(os.path.join(directory2, filename), 'r', encoding='utf8')
    data1 = parse(file1.read())
    data2 = parse(file2.read())
    return data1, data2

def align_sentences(sents1, sents2):
    '''
    sents1 and sents2 are SentenceLists (returned by get_data).
    Returns a list of aligned pairs of sentences and a list of a pair or lists,
    containing unaligned sentences from each user.
    '''
    i1 = 0
    i2 = 0
    n1 = len(sents1)
    n2 = len(sents2)
    aligned = []
    no_match = [[], []]

    while i1 < n1 or i2 < n2:
        if i1 >= n1:
            # ran out of sents1 but there are still sents2
            s2 = sents2[i2]
            print("No matching sentence from User 1 for {}".format(get_sentence_id(s2)))
            no_match[1].append(s2)
            i2 += 1
            continue
        elif i2 >= n2:
            # ran out of sents2 but there are still sents1
            s1 = sents1[i1]
            print("No matching sentence from User 2 for {}".format(get_sentence_id(s1)))
            no_match[0].append(s1)
            i1 += 1
            continue
        s1 = sents1[i1]
        s2 = sents2[i2]
        # [id1, 0] or [0, id2] or [id1, id1]
        m = match_sentences(s1, s2)
        if m[0] and m[1]:
#            print("Sentences {} and {} match with ids {}".format(i1, i2, m))
            # sentences match
            aligned.append((s1, s2))
            i1 += 1
            i2 += 1
        elif m[0]:
            # user2 skipped at least one; add s1 to no_match
            print("No matching sentence from User 2 for {}".format(m[0]))
            no_match[0].append(s1)
            i1 += 1
        else:
            # user1 skipped at least one; add s2 to no_match
            print("No matching sentence from User 1 for {}".format(m[1]))
            no_match[1].append(s2)
            i2 += 1
    return aligned, no_match

def get_sentence_id(sentence):
    id = sentence.metadata.get('sent_id')
    if not id:
        return False
    id = id.rpartition('_')[-1]
    match = ID_RE.match(id)
    if not match:
        False
    number, letter = match.groups()
    number = int(number)
    return number, letter

def id_compare(id1, id2):
    '''
    0 if id1 equals id2. Otherwise returns the index+1 of the lower one.
    ids are tuples: (int, char)
    '''
    if id1 == id2:
        return 0
    if id1[0] < id2[0]:
        return 1
    if id1[0] > id2[0]:
        return 2
    if id1[1] < id2[1]:
        return 1
    if id1[1] > id2[1]:
        return 2

def match_sentences(s1, s2):
    '''
    s1 and s2 are instances of TokenList.
    Returns False if sentences fail to match on basic features.
    '''
    id1 = get_sentence_id(s1)
    id2 = get_sentence_id(s2)
    idc = id_compare(id1, id2)
    results = [0, 0]
    if idc:
        # index+1 of the sentence with lower id, the one for the user who didn't skip one
        print("Sentences have different IDs: {} and {}!".format(id1, id2))
        ids = [id1, id2]
        results[idc-1] = ids[idc-1]
        return results
##    n1 = len(s1)
##    n2 = len(s2)
##    if n1 != n2:
##        print("Sentences have different lengths: {} and {}".format(n1, n2))
##        return results
##    for t1, t2 in zip(s1, s2):
##        id1 = t1.get('id')
##        id2 = t2.get('id')
##        form1 = t1.get('form')
##        form2 = t2.get('form')
##        if id1 != id2:
##            print("Sentence tokens have different IDs: {} and {}".format(id1, id2))
##            return results
##        if form1 != form2:
##            print("Sentence tokens have different forms: {} and {}".format(form1, form2))
##            return results
##        # Could check other Token features here: lemma, upos, xpos, feats, misc
    return [id1, id1]

def compare(spairs, write=''):
    result = []
    for sent1, sent2 in spairs:
        c1 = compare_annotations(sent1, sent2)
        if c1:
            result.append(c1)
    if write:
        with open(write, 'w', encoding='utf8') as file:
            for sentence in result:
                print(format_sentence_diffs(sentence), file=file)
    return result

def compare_annotations(s1, s2):
    '''
    s1 and s2 are the same sentence, annotated by two users.
    '''
    if len(s1) != len(s2):
        print("Lengths of {} and {} don't match!".format(s1, s2))
        return
    result = {}
    all_diffs = []
    for tok1, tok2 in zip(s1, s2):
        form = tok1.get('form')
        diffs = {}
        dep1 = tok1.get('deprel')
        dep2 = tok2.get('deprel')
        head1 = tok1.get('head')
        head2 = tok2.get('head')
        htok1 = get_token_by_id(s1, head1)
        if head1 != head2:
            htok2 = get_token_by_id(s2, head2)
            diffs['head'] = (htok1, htok2)
        if dep1 != dep2:
            diffs['dep'] = (dep1, dep2)
            if 'head' not in diffs:
                diffs['head'] = htok1
        if diffs:
            diffs['form'] = form
            all_diffs.append(diffs)
    if all_diffs:
        sid = get_sentence_id(s1)
        text = s1.metadata.get('text')
        result['sentence'] = "{}{}:{}".format(sid[0], sid[1], text)
        result['diffs'] = all_diffs
    return result

def get_token_by_id(sentence, id):
    for token in sentence:
        i = token.get('id')
        if i == id:
            return token.get('form')
    return

def format_diffs(diffs):
    '''
    diffs is a dict with keys "form", "head" and "dep"
    '''
    form = diffs.get('form')
    head = diffs.get('head')
    if isinstance(head, tuple):
        head = "{}|{}".format(head[0], head[1])
        return "{} <--- {}".format(form, head)
    if 'dep' in diffs:
        dep = diffs['dep']
        arc = "<--{}|{}--".format(dep[0], dep[1])
#    else:
#        arc = "<----"
        return "{} {} {}".format(form, arc, head)

def format_sentence_diffs(sentence):
    label = sentence['sentence']
    diffs = sentence['diffs']
    string = '\n' + label
    for diff in diffs:
        string += "\n  {}".format(format_diffs(diff))
    return string

