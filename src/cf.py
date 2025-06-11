"""
Combine features in a CoNNL-U file so that for words that are segmented by
HornMorpho all features are associated with stems rather than affixes.
"""

def combine_feats(path, outpath=''):
    """
    path: path to conllu file.
    outpath: where to write the resulting file. If empty, generated
       automatically.
    """
    output = []
    in_segmented = False
    id_range = None
    saved_feats = set()
    saved_lines = []
    saved_head = -1
    with open(path) as file:
        for line in file:
            line = line.strip()
            if not line or line[0] == '#':
                output.append(line)
            else:
                items = line.split('\t')
                feats = items[5]
                id = items[0]
                tok = items[1]
                rel = items[7]
                is_group = '-' in id
                if not is_group:
                    id = int(id)
                if in_segmented:
                    if is_group or id < id_range[0] or id > id_range[1]:
                        # End of segmented word
                        # Add saved stuff
#                        print("saved head {}, saved feats {}".format(saved_head, saved_feats))
                        for saved_line in saved_lines:
                            if int(saved_line[0]) == saved_head:
                                # This is the head
                                # Fix feats
                                if saved_feats:
                                    saved_feats = list(saved_feats)
                                    saved_feats.sort()
                                    saved_feats = '|'.join(saved_feats)
                                    saved_line[5] = saved_feats
                                else:
                                    saved_line[5] = '_'
                            else:
                                saved_line[5] = '_'
                            output.append('\t'.join(saved_line))
                        saved_lines = []
                        saved_feats = set()
                        saved_head = -1
                        if is_group:
                            in_segmented = True
                            id_range = id.split('-')
                            id_range = int(id_range[0]), int(id_range[1])
                        else:
                            in_segmented = False
                            id_range = None
                        # Add current line
                        output.append(line)
                    else:
                        # current token is in segmented word
                        exp_feats = update_feats(feats, tok, rel)
                        if exp_feats:
                            saved_feats.update(exp_feats)
                        if is_head(items, id_range):
                            saved_head = id
                        saved_lines.append(items)
                elif is_group:
                    in_segmented = True
                    id_range = id.split('-')
                    id_range = int(id_range[0]), int(id_range[1])
                    output.append(line)
                else:
                    output.append(line)
    outpath = outpath or path.rpartition('.')[0] + '_cf.conllu'
    with open(outpath, 'w') as file:
        for line in output:
            print(line, file=file)
#    return output

def update_feats(feats, token, rel):
    if feats == '_':
        return None
    feats = feats.split('|')
    if 'Possessive=Yes' in feats or rel == 'det:poss':
        new_feats = []
        # possessive, modify PNG
        for feat in feats:
            f, v = feat.split('=')
            if f == 'Gender':
                new_feats.append("Gender[psor]={}".format(v))
            elif f == 'Person':
                new_feats.append("Person[psor]={}".format(v))
            elif f == 'Number':
                new_feats.append("Number[psor]={}".format(v))
            elif f not in ('PronType', 'Possessive'):
                new_feats.append(feat)
        return new_feats
    elif rel == "obj:aff":
        new_feats = []
        for feat in feats:
            f, v = feat.split('=')
            if f == 'Gender':
                new_feats.append("ObjGen={}".format(v))
            elif f == 'Number':
                new_feats.append("ObjNum={}".format(v))
            elif f == 'Person':
                new_feats.append("ObjPers={}".format(v))
            elif f not in ['PronType', 'Case']:
                new_feats.append(feat)
        return new_feats
    elif rel == 'obl:aff':
        new_feats = []
        pre = "Mal"
        if token.startswith("ለ") or token.startswith("ል"):
            pre = "Ben"
        for feat in feats:
            f, v = feat.split('=')
            if f == 'Gender':
                new_feats.append("{}Gen={}".format(pre, v))
            elif f == 'Number':
                new_feats.append("{}Num={}".format(pre, v))
            elif f == 'Person':
                new_feats.append("{}Pers={}".format(pre, v))
            elif f not in ['PronType', 'Case']:
                new_feats.append(feat)
        return new_feats
    else:
        new_feats = []
        for feat in feats:
            f, v = feat.split('=')
            if f != 'PronType':
                new_feats.append(feat)
        return new_feats

def is_head(c_fields, id_range):
    id = int(c_fields[0])
    head = c_fields[6]
    if head == '_':
        head = -1
    else:
        head = int(head)
    if id_range[0] <= head <= id_range[1]:
        return False
    return True

