'''
Conversion between raw sentence strings and empty CoNLL-U representations.
Other simple file processing utils.
Author: Michael Gasser
2023, 2024
'''

import ntpath
import os
import re

MWE_RE = re.compile(r"(\w+)\s*[=:]\s*\(([\w\s]+)\)")

def tokenize(string):
    '''
    string is a tokenized sentence, which may contain segmented words or MWEs, indicated like this:
    ከዘመዶቻችን: (ከ ዘመድ ኦች ኣችን)
    '''
    tokens = []
    while string:
        if match := MWE_RE.match(string):
            groups = match.groups()
            end = match.end()
            tokens.append((groups[0], groups[1].split()))
            string = string[end:].strip()
        else:
            partition = string.partition(' ')
            token = partition[0]
            tokens.append(token)
            string = partition[-1]
    return tokens

def tokenfile2conllu(file, write2=None):
    '''Convert a file with sentence strings to a string of CoNLL-U representations.'''
    conllu = []
    with open(file, encoding='utf8') as f:
        sent_id = ''
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line[0] == '#':
                # this is a sentence id
                sent_id = line.split('#')[1].strip()
            else:
                tokens = tokenize(line)
                c = tokens2conllu(tokens, sent_id=sent_id)
                conllu.append(c)
                sent_id = ''
    conllu = "\n\n".join(conllu)
    if write2:
        with open(write2, 'w', encoding='utf8') as f:
            print(conllu, file=f)
    else:
        return conllu

def tokens2conllu(tokens, sentence='', comment='', sent_id=''):
    '''
    tokens is a list of strings and tuples consisting of a string and a list of segments.
    '''
    index = 1
    lines = []
    sentence = sentence or ' '.join([t[0] if isinstance(t, tuple) else t for t in tokens])
    if comment:
        lines.append(comment)
    if sent_id:
        lines.append("# sent_id = {}".format(sent_id))
    lines.append("# text = {}".format(sentence))
    for token in tokens:
        if isinstance(token, tuple):
            # A multi-token 'word'
            mt = token[0]
            segments = token[1]
            length = len(segments)
            start = index
            end = index + length-1
            multi = "{}-{}\t{}\t_\t_\t_\t_\t_\t_\t_\t_".format(start, end, mt)
            lines.append(multi)
            for segment in segments:
                segline = "{}\t{}\t_\t_\t_\t_\t_\t_\t_\t_".format(index, segment)
                lines.append(segline)
                index += 1
        else:
            line = "{}\t{}\t_\t_\t_\t_\t_\t_\t_\t_".format(index, token)
            lines.append(line)
            index += 1
    return '\n'.join(lines)

def conllu2corpus(conllu, fileout):
    lines = []
    with open(conllu, encoding='utf8') as infile:
        for line in infile:
            line = line.strip()
            if line and line[0] == '#':
                if "sent_id" in line:
                    line = line.split("sent_id = ")[-1]
                    lines.append("# {}".format(line))
                elif "text =" in line:
                    line = line.split("text = ")[-1]
                    lines.append(line)
    if fileout:
        with open(fileout, 'w', encoding='utf8') as outfile:
            for line in lines:
                print(line, file=outfile)
    else:
        return lines

def number_sentences(pathin, pathout, prefix):
    with open(pathout, 'w', encoding='utf8') as outfile:
        with open(pathin, encoding='utf8') as infile:
            for index, line in enumerate(infile):
                id = "{}_{}".format(prefix, index+1)
                print("# {}".format(id), file=outfile)
                print(line, file=outfile)

def corpus2conllu(path, lemma_is_token=True, write=False, write_dir='',
                  comment_lines=True, debug=False):
    '''
    Convert the sentences in file at path, one sentence per line, to empty CoNLL-U strings.
    If write is True, write the CoNNL-U strings to a file, creating a filename from the
    source filename.
    If write_dir is not empty, create the file in that directory.
    If write is False, return the list of CoNLL-U strings.
    If lemma_is_token is True, copy each token's form string in the CoNLL-U lemma field.
    '''
    rfilename = ntpath.basename(path).split(".")[0]
    conllu = []
    with open(path, encoding='utf8') as infile:
        conllu = sentences2conllu(infile.readlines(), rfilename, lemma_is_token=lemma_is_token,
                                                             comment_lines=comment_lines, debug=debug)
    if write:
        wfilename = rfilename + ".conllu"
        wpath = os.path.join(write_dir, wfilename) if write_dir else wfilename
        with open(wpath, 'w', encoding='utf8') as outfile:
            for sentence in conllu:
                print(sentence, file=outfile)
    else:
        return conllu

def tsv2conllu(file, drop=None, write=False):
    '''
    Drop may be a list of column indices.
    '''
    corpus = []
    alts = []
    with open(file, encoding='utf8') as f:
        for line in f:
            if line[0] != '#':
                # Must be the initial line, with column headings
                continue
            columns = line.strip().split('\t')
            if drop:
                cols = []
                for index, c in enumerate(columns):
                    if index not in drop:
                        cols.append(c)
            else:
                cols = columns
            if len(cols) != 2:
                print("** Something wrong with {}".format(line))
                return
            sentence = cols[1]
            comment = cols[0]
            sentence_split = sentence.split('/')
            sentence = sentence_split[0]
            if len(sentence_split) > 1:
                alts.append((comment, sentence_split[1:]))
            conllu = sentence2conllu(sentence, None, 0, comment=comment)
            corpus.append(conllu)
    if write:
        with open("../treebanks/" + write, 'w', encoding='utf8') as f:
            for c in corpus:
                print(c, file=f)
    return corpus

def sentences2conllu(sentences, corpus, lemma_is_token=True, comment_lines=True, debug=False):
    '''
    Convert a list of sentences to a list of CoNLL-U strings.
    '''
    output = []
    alts = []
    sindex = 0
    
    if comment_lines:
        # Every other line is a comment, so group the sentences in pairs
        comments = sentences[::2]
        sents = sentences[1::2]
        for comment, sentence in zip(comments,sents):
#            print("c: {}".format(comment))
#            print("s: {}".format(sentence))
            comment = comment.strip()
            sentence = sentence.strip()
            if comment[0] != '#':
                print("{} doesn't begin with #".format(comment))
                break
            if sentence[0] == '#':
                print("{} begins with #".format(sentence))
                break
            comment = comment[1:].strip()
            # There may be alternative sentences; if so, use the first one, saving the others in alts
            sentence_split = sentence.split('/')
            sentence = sentence_split[0]
            if len(sentence_split) > 1:
                alts.append((comment, sentence_split[1:]))
            output.append(sentence2conllu(sentence, corpus, sindex+1, lemma_is_token=lemma_is_token,
                                                                            comment=comment))
            sindex += 1
    else:
        for sentence in sentences:
            # Strip off newline char if there is one.
            sentence = sentence.strip()
            if debug:
                print(sentence)
            output.append(sentence2conllu(sentence, corpus, sindex+1, lemma_is_token=lemma_is_token))
            sindex += 1
    return output

def sentence2conllu(sentence, corpus, sindex, lemma_is_token=True, comment=''):
    '''
    Convert a sentence in the form of a string with spaces separating tokens
    to an empty CoNLL-U string.
    '''
    endpunc = ["።", "?", "!"]
    sentence_split = sentence.split('#')
    sentence = sentence_split[0].strip()
    sent_id = comment if comment else "{}_{}".format(corpus, sindex)
    output = "# text = {}\n# sent_id = {}\n".format(sentence, sent_id)
    if len(sentence_split) > 1:
        sent_comment = ';'.join(sentence_split[1:])
        output += "# comment = {}\n".format(sent_comment)
    # Check end punctuation
    last_char = sentence[-1]
    if last_char not in endpunc:
        print(comment, sentence)
    # Make sure there's a space before the end punctuation
    if sentence[-2] != ' ':
      sentence = sentence[:-1] + ' ' + last_char
#        print(sentence)
    tokens = sentence.split()
    for index, token in enumerate(tokens):
        lemma = token if lemma_is_token else '_'
        output += "{}\t{}\t{}\t_\t_\t_\t_\t_\t_\t_\n".format(index+1, token, lemma)
    return output

def conllu_corpus2sentences(path, name='', write=False, write_dir=''):
    '''
    Convert the ConLLU representations in file at path to a list of raw sentences.
    If write is True, write the sentences to a file, creating a filename from the
    source filename.
    If write_dir is not empty, create the file in that directory.
    '''
    filename = ntpath.basename(path).split(".")[0]
    name = name or filename
    with open(path, encoding='utf8') as infile:
        conllus = infile.read().split('\n\n')
    sentences = conllus2sentences(conllus)
    if write:
        wfilename = name + ".txt"
        wpath = os.path.join(write_dir, wfilename) if write_dir else wfilename
        with open(wpath, 'w', encoding='utf8') as outfile:
            for sentence in sentences:
                print(sentence, file=outfile)
    else:
        return sentences

def conllus2sentences(conllus):
    '''
    conllus is a list of CoNLL-U string representations.
    Returns a list of sentence strings.
    '''
    return [conllu2sentence(conllu) for conllu in conllus if conllu]

def conllu2sentence(conllu, include_id=True):
    '''
    conllu is a CoNLL-U string representation of a single sentence.
    Returns the sentence, assuming it follows # text = in the first line of the string.
    '''
    conllu = conllu.split("\n")
    lines = []
    for line in conllu:
        if "# sent_id =" in line:
            lines.append("# " + line.split("sent_id =")[-1].strip())
        elif "# text =" in line:
            lines.append(line.split("text = ")[-1].strip())
    if not lines:
        print("CoNLL-U  representation {} doesn't start contain a text string!".format(conllu))
    return '\n'.join(lines)

def align_sentences(file1, file2, comments=True, write="ti_am_att-ud-text.txt"):
    '''
    Attempt to align the raw sentences in the two files.
    '''
    lines1 = []
    lines2 = []
    with open(file1, encoding='utf8') as f1:
        for line in f1:
            line = line.strip()
            if not line:
                continue
            if comments and line[0] == '#':
                lines1.append(line)
            else:
                lines1[-1] += "\n" + line
    with open(file2, encoding='utf8') as f2:
        for line in f2:
            line = line.strip()
            if not line:
                continue
            if comments and line[0] == '#':
                lines2.append(line)
            else:
                lines2[-1] += "\n" + line
    n1 = len(lines1)
    n2 = len(lines2)
    if n1 == n2:
        with open(write, 'w', encoding='utf8') as file:
            for l1, l2 in zip(lines1, lines2):
                c1, s1 = l1.split("\n")
                c2, s2 = l2.split("\n")
                if c1 != c2:
                    print("{} and {} don't match".format(l1, l2))
                print("{}\n{}\n{}".format(c1, s1, s2), file=file)
#    print("N1 {}, N2 {}".format(n1, n2))
