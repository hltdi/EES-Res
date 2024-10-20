'''
Modifying CoNNL-U files in various ways.
'''

from conllu import parse, TokenList, Token

def read_file(path):
    file = open(path, 'r', encoding='utf8')
    data = parse(file.read())
    return data

def distribute_feats1(sent, source_id, dest_id, feats):
    pass

def get_token_by_id(sentence, id):
    for token in sentence:
        if token['id'] == id:
            return token
    return

def get_feat_diffs(ssent, dsent):
    ids = []
    for st, dt in zip(ssent, dsent):
        if st['id'] == dt['id'] and st['feats'] != dt['feats'] and st['form'] == dt['form']:
            print(st['id'], st['form'], st['feats'], dt['feats'])
            ids.append(st['id'])
    return ids

def copy_feats(destsent, sourcesent, sourceids, destids=None):
    destids = destids or sourceids
    for si, di in zip(sourceids, destids):
        srctoken = get_token_by_id(sourcesent, si)
        desttoken = get_token_by_id(destsent, di)
        desttoken['feats'] = srctoken['feats']
                
def all_distribute_feats(syn, morph):
    '''
    syn is a complete CoNNL-U representation, with feats on the heads of words.
    morph is a morphology-only CoNNL-U representation, with feats distributed.
    '''
    for s, m in zip(syn, morph):
        start = -1
        length = -1

def split_token(sentence, wid, tokens, headid=0, rel=None, upos=None, xpos=None, head=None, feats=None, lemma=None):
    length = len(tokens)
    morphs = []
    tokindex = 0
    for index, word in enumerate(sentence):
        id = word.get('id')
        if isinstance(id, tuple):
            id_start, id_end = id[0], id[2]
            if id_end < wid:
                continue
            else:
                word['id'] = (id_start+length-1, '-', id_end+length-1)
        elif id < wid:
            continue
        elif id == wid:
            tokindex = index
            # the group token
            tokhead = word['id']
            word['id'] = (wid, '-', wid+length-1)
            word['lemma'] = None
            word['upos'] = None
            word['xpos'] = None
            word['deprel'] = None
            word['head'] = None
            word['feats'] = None
            # the morphemes in the split token
            for i, tok in enumerate(tokens):
                morph = Token()
                morph['id'] = wid + i
                morph['form'] = tok
                morph['lemma'] = lemma[i] if lemma else None
                morph['upos'] = upos[i] if upos else None
                morph['xpos'] = xpos[i] if xpos else morph['upos']
                morph['feats'] = feats[i] if feats else None
                morph['head'] = tokhead if i == headid else wid
                morph['deprel'] = rel[i] if rel else None
                morph['deps'] = None
                morph['misc'] = None
                morphs.append(morph)
        else:
            # follows split word
            word['id'] = id + length-1
    sentence[tokindex+1:tokindex+1] = morphs

def merge_token(sentence, ids, rel=None, upos=None, xpos=None, head=None, feats='', lemma=None):
    start, end = ids
    diff = end - start
    to_del = []
    merged_word = None
    for index, word in enumerate(sentence):
        id = word.get('id')
        if isinstance(id, tuple):
            id_start, id_end = id[0], id[2]
            if id_start == start:
                merge_word = word
                # Make this token the merged one
                word['id'] = start
                word['lemma'] = lemma
                word['upos'] = upos
                word['xpos'] = xpos or upos
                word['deprel'] = rel
                word['head'] = head
                word['feats'] = feats
            elif id_start < start:
                # MW token is before merged token; don't change
                continue
            else:
                word['id'] = (id_start - diff, '-', id_end - diff)
        elif id < start:
            # token comes before merged part, so don't change its id
            # but its head might have changed
            head = word['head']
            if start <= head <= end:
                word['head'] = start
            elif head > end:
                word['head'] -= diff
        elif start <= id <= end:
            # token comes within merged part
            # see if it's the head of the merged part
            whead = word['head']
            if whead < start or whead > end:
                # this must be the head
                if not merge_word['lemma']:
                    merge_word['lemma'] = word['lemma']
                if not merge_word['upos']:
                    merge_word['upos'] = word['upos']
                if not merge_word['xpos']:
                    merge_word['xpos'] = word['xpos']
                mwfeats = merge_word['feats']
                if not mwfeats and mwfeats != None:
                    merge_word['feats'] = word['feats']
                if not merge_word['deprel']:
                    merge_word['deprel'] = word['deprel']
                if whead > end:
                    merge_word['head'] = whead - diff
                else:
                    merge_word['head'] = whead
            to_del.append(index)
        else:
            # token comes after merged part
            word['id'] -= diff
            whead = word['head']
            if whead > start:
                # token's head must be adjusted
                if whead <= end:
                    # token is within merged token; make it equal to start
                    word['head'] = start
                else:
                    # token is after merged token; subtract merge length - 1
                    word['head'] -= diff
    for ti in reversed(to_del):
        del sentence[ti]

def fix(data, move_features=True, move_misc=True):
    for s in data:
        fix_sentence(s, move_features=move_features, move_misc=move_misc)

def fix_rels(data):
    for s in data:
        fix_sentence_rels(s)

def fix_sentence_rels(sentence):
    position = 1
    mwe = []
    for word in sentence:
        id = word.get('id')
        if isinstance(id, tuple):
            # this is an empty MWE
            mwe = id[0], id[2]
            # don't increment position, following words are segments
            continue
#        wdict = {}
        head = word.get('head', 0)
        rel = word.get('deprel')
#        wdict['head'] = head
#        wdict['whead'] = True
        sub = False
        whead = True
        if mwe:
            if position > mwe[1]:
                mwe = []
            else:
                # part of a word
                sub = True
                if mwe[0] <= head <= mwe[1]:
                    # this part's head is within the word, so it's not the head
                    whead = False
                    subhead = head
                    if id < subhead and rel not in ('compound', 'dep:lvc'):
                        # prefix
                        word['deprel'] += ':pre'
                        word['xpos'] = word['upos'] + ':pre'
                    else:
                        word['deprel'] += ':suf'
                        word['xpos'] = word['upos'] + ':suf'
                elif word['upos'] == 'VERB':
                    # the head of the word
                    word['xpos'] = 'VSTEM'
        position += 1

def write(data, path):
    with open(path, 'w', encoding='utf8') as file:
        for sentence in data:
            string = sentence.serialize()
            print(string, file= file, end='')

def fix_sentence(sentence, move_features=True, move_misc=True):
    props = []
    mwe = []
    position = 1
    wordhead = 0
    move_feats = []
    words_by_id = []
    misc_words = {}
    for word in sentence:
        id = word.get('id')
        if isinstance(id, tuple):
            # this is an empty MWE
            mwe = id[0], id[2]
            # don't increment position, following words are segments
            continue
        wdict = {}
        head = word.get('head', 0)
        wdict['head'] = head
        wdict['whead'] = True
        if mwe:
            if position > mwe[1]:
                mwe = []
                wdict['sub'] = False
            else:
                # part of a word
                wdict['sub'] = True
                if mwe[0] <= head <= mwe[1]:
                    # this part's head is within the word, so it's not the head
                    wdict['whead'] = False
        else:
            wdict['sub'] = False
        feats = word.get('feats')
        wdict['feats'] = feats
        misc = word.get('misc')
        wdict['misc'] = misc
        if misc:
            misc_words[id] = misc
        wdict['form'] = word.get('form')
        if feats and not wdict['whead']:
            # add to move feats
            move_feats.append((feats, id, head))
        props.append(wdict)
        words_by_id.append(word)
        position += 1
    if move_features:
        for f, old, new in move_feats:
            old_word = words_by_id[old-1]
            new_word = words_by_id[new-1]
            print("Moving feats from {} to {}".format(old_word, new_word))
            old_word['feats'] = None
            new_feats = new_word.get('feats')
            if new_feats:
                new_feats.update(f)
            else:
                new_word['feats'] = f
    if move_misc:
        if misc_words:
            print("misc {}".format(misc_words))
        for id, feats in misc_words.items():
            word = words_by_id[id-1]
            word['misc'] = None
            f = word.get('feats')
            if f:
                f.update(feats)
            else:
                word['feats'] = feats
    return props
