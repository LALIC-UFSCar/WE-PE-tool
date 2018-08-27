#!/usr/bin/env python3
import subprocess
import re
import os
import random
import string
import nltk.translate.ibm2 as align
from readers.read_blast import BlastReader

BLAST_PATH = '../FAPESP_MUSE_test-a.blast'
TW_SZ = 5
ERRORS = ['lex-incTrWord', 'lex-notTrWord']


def tag_sentences(src, sys):
    src_out = run_apertium_tagger(src, 'en')
    sys_out = run_apertium_tagger(sys, 'pt')

    assert len(src_out) == len(sys_out)
    num_sents = len(src_out)

    src_tags = list()
    sys_tags = list()
    for i in range(num_sents):
        src_tokens = re.findall(r'\^([^$]*)\$', src_out[i])
        sys_tokens = re.findall(r'\^([^$]*)\$', sys_out[i])
        src_tags.append([re.findall(r'([^<>]+|^>$)', token)
                         for token in src_tokens])
        sys_tags.append([re.findall(r'([^<>]+|^>$)', token)
                         for token in sys_tokens])

    return list(zip(src_tags, sys_tags))


def run_apertium_tagger(lines, lang):
    application_path = str(os.path.abspath(os.path.curdir))
    out_lines = list()

    for line in lines:
        p = subprocess.Popen([application_path + '/apertium/parse_file.sh', '--lang', lang],
                             stdin=subprocess.PIPE, universal_newlines=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL)
        out = p.communicate(' '.join(line))
        out_lines.append(out[0])
    return out_lines


def extract_features(tagged_sent, alignment, tw_size, target):
    tagged_src = tagged_sent[0]
    tagged_sys = tagged_sent[1]
    alignment = list(alignment)

    lct_src_index = list()
    lct_sys_index = list()

    # Get LCT
    if target == 'correct':
        while not lct_sys_index or None in lct_sys_index:
            lct_src_index = random.choice(range(len(tagged_src)))
            # Get sys LCT by alignment
            lct_sys_index = [a[1] for a in alignment if a[0] == lct_src_index]

        if len(lct_sys_index) < 3:
            lct_sys_index = lct_sys_index[0]
        else:
            lct_sys_index = lct_sys_index[len(lct_sys_index) // 2]
    else:
        lct_src_index = target[0]
        lct_sys_index = target[1]

        # Indices where one has MWE
        has_mw_src = [(i, w[0].count(' '))
                      for (i, w) in enumerate(tagged_src) if ' ' in w[0]]
        has_mw_sys = [(i, w[0].count(' '))
                      for (i, w) in enumerate(tagged_sys) if ' ' in w[0]]
        # If BLAST aligned word is after the MWE
        # Needs to discount how many spaces are being ignored in the tagged sentences
        if has_mw_src:
            for (i, num_spaces) in has_mw_src:
                lct_src_index = [lct if lct <=
                                 i else lct - num_spaces for lct in lct_src_index]
        if has_mw_sys:
            for (i, num_spaces) in has_mw_sys:
                lct_sys_index = [lct if lct <=
                                 i else lct - num_spaces for lct in lct_sys_index]

        # Ignore sentences without alignment
        if -1 in lct_src_index:
            return None
        if -1 in lct_sys_index:
            return None

        if len(lct_sys_index) < 3:
            lct_sys_index = lct_sys_index[0]
        else:
            lct_sys_index = lct_sys_index[len(lct_sys_index) // 2]

        if len(lct_src_index) < 3:
            lct_src_index = lct_src_index[0]
        else:
            lct_src_index = lct_src_index[len(lct_src_index) // 2]

    # Get TW
    src_tw_start = max(lct_src_index - (tw_size // 2), 0)
    src_tw_end = min(lct_src_index + (tw_size // 2) + 1, len(tagged_src))
    src_tw = tagged_src[src_tw_start: src_tw_end]

    sys_tw_start = max(lct_sys_index - (tw_size // 2), 0)
    sys_tw_end = min(lct_sys_index + (tw_size // 2) + 1, len(tagged_sys))
    sys_tw = tagged_sys[sys_tw_start: sys_tw_end]

    # Compute features
    features = dict()

    # Features src
    features['srcSize'] = len(tagged_src)
    features['engPossessive'] = bool([w for w in tagged_src if 'pos' in w])

    # Features sys
    features['sysSize'] = len(tagged_sys)

    for (i, tok) in enumerate(sys_tw):
        # Gender
        key = ''
        if i < tw_size // 2:
            key = 'genToken{}BefSys'.format(i + 1)
        elif i == tw_size // 2:
            key = 'genSysToken'
        else:
            key = 'genToken{}AftSys'.format(i - (tw_size // 2))
        features[key] = 'f' if 'f' in tok else 'm' if 'm' in tok else 'NC'

        # Number
        if i < tw_size // 2:
            key = 'numToken{}BefSys'.format(i + 1)
        elif i == tw_size // 2:
            key = 'numSysToken'
        else:
            key = 'numToken{}AftSys'.format(i - (tw_size // 2))
        features[key] = 'sg' if 'sg' in tok else 'pl' if 'pl' in tok else 'NC'

    features['SysTokenTag'] = True if len(
        tagged_sys[lct_sys_index]) > 1 else False
    features['sysBegCap'] = True if tagged_sys[lct_sys_index][0][0].isupper() else False

    # Features sys and src
    for (i, tok) in enumerate(src_tw):
        key = ''
        tok_tags = re.sub(r'_\+[^_$]+_', '+', '_'.join(tok[1:]))
        if i < tw_size // 2:
            key = 'posToken{}BefSrc'.format(i + 1)
        elif i == tw_size // 2:
            key = 'posSrcToken'
        else:
            key = 'posToken{}AftSrc'.format(i - (tw_size // 2))
        features[key] = tok_tags if tok_tags else 'NC'

    for (i, tok) in enumerate(sys_tw):
        key = ''
        tok_tags = re.sub(r'_\+[^_$]+_', '+', '_'.join(tok[1:]))
        if i < tw_size // 2:
            key = 'posToken{}BefSys'.format(i + 1)
        elif i == tw_size // 2:
            key = 'posSrcToken'
        else:
            key = 'posToken{}AftSys'.format(i - (tw_size // 2))
        features[key] = tok_tags if tok_tags else 'NC'

    try:
        if re.match('vb[^_]+', '_'.join(tagged_src[lct_src_index][1:])):
            features['verbSrc'] = re.sub(
                'vb[^_]+_', '', '_'.join(tagged_src[lct_src_index][1:]))
        else:
            features['verbSrc'] = 'NC'
    except IndexError:
        features['verbSrc'] = 'NC'

    try:
        if re.match('vb[^_]+', '_'.join(tagged_sys[lct_sys_index][1:])):
            features['verbSys'] = re.sub(
                'vb[^_]+_', '', '_'.join(tagged_sys[lct_sys_index][1:]))
        else:
            features['verbSys'] = 'NC'
    except IndexError:
        features['verbSys'] = 'NC'

    # Features sys/src
    features['srcSysRatio'] = len(tagged_src) / len(tagged_sys)

    num_verbs_src = 0
    num_nouns_src = 0
    for tok in tagged_src:
        try:
            if re.match('vb[^_]+', '_'.join(tok[1:])):
                num_verbs_src += 1
            elif 'n' in tok[1:]:
                num_nouns_src += 1
        except IndexError:
            pass

    num_verbs_sys = 0
    num_nouns_sys = 0
    for tok in tagged_sys:
        try:
            if re.match('vb[^_]+', '_'.join(tok[1:])):
                num_verbs_sys += 1
            elif 'n' in tok[1:]:
                num_nouns_sys += 1
        except IndexError:
            pass

    features['srcSysVRatio'] = max(num_verbs_src, 1) / max(num_verbs_sys, 1)
    features['srcSysNRatio'] = max(num_nouns_src, 1) / max(num_nouns_sys, 1)

    # Remove * from start of lct if exists
    flat_lct_src = re.sub('\*', '', tagged_src[lct_src_index][0])
    flat_lct_sys = re.sub('\*', '', tagged_sys[lct_sys_index][0])

    features['equalTokenSrcSys'] = flat_lct_src == flat_lct_sys
    special_char_src = flat_lct_src in string.punctuation or 'num' in tagged_src[lct_src_index]
    special_char_sys = flat_lct_sys in string.punctuation or 'num' in tagged_sys[lct_sys_index]
    features['specialCharSrcSys'] = special_char_src and special_char_sys

    return features


def main():
    blast_reader = BlastReader(BLAST_PATH)
    bitexts = list()
    src_lines = list()
    sys_lines = list()
    target = list()

    # Correct sentences
    for i in blast_reader.get_correct_indices():
        if i <= 300:
            src_lines.append(blast_reader.src_lines[i])
            sys_lines.append(blast_reader.sys_lines[i])
            target.append('correct')

    # Error lines
    for (line, error) in blast_reader.get_filtered_errors(ERRORS):
        if line <= 300:
            src_lines.append(blast_reader.src_lines[line])
            sys_lines.append(blast_reader.sys_lines[line])
            target.append(error)

    # Tag sentences
    tagged_lines = tag_sentences(src_lines, sys_lines)

    # Align sentences
    for sent in tagged_lines:
        bitexts.append(align.AlignedSent(
            [w[0] for w in sent[0]], [w[0] for w in sent[1]]))
    align.IBMModel2(bitexts, 15)

    for (i, sent) in enumerate(tagged_lines):
        features = extract_features(
            sent, bitexts[i].alignment, TW_SZ, target[i])
        print(features)


if __name__ == '__main__':
    main()