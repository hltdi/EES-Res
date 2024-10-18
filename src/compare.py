from conllu import parse, TokenList, Token
import os, re

DIR = "../treebanks/"

USERS = ['megasser', 'abutihere', 'nazarethamlesom']

ID_RE = re.compile(r'(\d+)([a-zA-Z]*)')

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

