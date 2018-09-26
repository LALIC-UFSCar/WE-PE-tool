import tempfile
import os
import subprocess
import re
import random
import string
from readers.read_blast import BlastReader
from readers.read_giza import GIZAReader


class ErrorIdentification(object):

    def __init__(self):
        self.TW_SZ = 5

    def train(self, blast_filename, model_type, error_types=None):
        blast_reader = BlastReader(blast_filename)
        src_lines = list()
        sys_lines = list()
        target = list()

        # Files for GIZA
        src_fd, src_filename = tempfile.mkstemp(text=True)
        sys_fd, sys_filename = tempfile.mkstemp(text=True)
        src_file = open(src_filename, 'w')
        sys_file = open(sys_filename, 'w')

        # Correct sentences
        for i in blast_reader.get_correct_indices():
            src_lines.append(blast_reader.src_lines[i])
            sys_lines.append(blast_reader.sys_lines[i])
            target.append('correct')

            # Write files for GIZA
            src_file.write(' '.join(blast_reader.src_lines[i]))
            src_file.write('\n')
            src_file.write(' '.join(blast_reader.sys_lines[i]))
            src_file.write('\n')

        # Error sentences
        errors = blast_reader.get_filtered_errors(
            error_types) if error_types else blast_reader.error_lines
        for (line, error) in errors:
            src_lines.append(blast_reader.src_lines[line])
            sys_lines.append(blast_reader.sys_lines[line])
            target.append(error)

            src_file.write(' '.join(blast_reader.src_lines[line]))
            src_file.write('\n')
            src_file.write(' '.join(blast_reader.sys_lines[line]))
            src_file.write('\n')
        src_file.close()
        sys_file.close()
        os.close(src_fd)
        os.close(sys_fd)

        # Tag sentences
        tagged_lines = self.tag_sentences(src_lines, sys_lines)

        # Align sentences
        alignments = self.align_sentences(src_filename, sys_filename)

        # Extract features
        training_instances = list()
        for (i, sent) in enumerate(tagged_lines):
            features = self.extract_features(
                sent, alignments[i]['alignment'], self.TW_SZ, target[i])
            if features:
                training_instances.append(features)

    def tag_sentences(self, src, sys):
        """Tags all sentences from src and sys

        Arguments:
            src {list} -- Source language lines
            sys {list} -- Machine Translation output lines

        Returns:
            list -- List of tuples with aligned tagged lines. Tags are in a list
        """
        src_out = self.run_apertium_tagger(src, 'en')
        sys_out = self.run_apertium_tagger(sys, 'pt')

        num_sents = len(src_out)
        src_tags = list()
        sys_tags = list()
        for i in range(num_sents):
            src_tokens = re.findall(r'\^([^$]*)\$', src_out[i])
            sys_tokens = re.findall(r'\^([^$]*)\$', sys_out[i])

            # Replace crf tokens with $
            src_tokens = ['$' if w == 'crf' else w for w in src_tokens]
            sys_tokens = ['$' if w == 'crf' else w for w in sys_tokens]

            src_tags.append([re.findall(r'([^<>]+|^>$)', token)
                             for token in src_tokens])
            sys_tags.append([re.findall(r'([^<>]+|^>$)', token)
                             for token in sys_tokens])

        return list(zip(src_tags, sys_tags))

    def run_apertium_tagger(self, lines, lang):
        """Creates a subprocess to run the Apertium Tagger via the `apertium/parse_file.sh` script

        Arguments:
            lines {list} -- List of lines to be tagged
            lang {str} -- Language to run the tagger with

        Returns:
            list -- Returns a list with all tagged lines in the Apertium format
        """
        apertium_script_path = 'src/apertium/parse_file.sh'
        out_lines = list()

        for line in lines:
            proc = subprocess.Popen([apertium_script_path, '--lang', lang],
                                    stdin=subprocess.PIPE, universal_newlines=True,
                                    stdout=subprocess.PIPE)
            out = proc.communicate(' '.join(line))
            out_lines.append(out[0])
        return out_lines

    def align_sentences(self, src, sys):
        giza_script_path = 'src/aligner/align_sentences.sh'
        proc = subprocess.Popen([giza_script_path,
                                 '--srcpath', src,
                                 '--syspath', sys],
                                stdout=subprocess.PIPE)
        out = proc.communicate()
        num_sents = int(out[0])
        giza_reader = GIZAReader('tmp/giza.output')
        return giza_reader.aligned_lines[:num_sents]

    def extract_features(self, tagged_sent, alignment, tw_size, target):
        """Generates the features for the identification given the tagged sentence pair,
        the alignment between them, the window size and a specification of the error
        corresponding to them

        Arguments:
            tagged_sent {tuple} -- Tuple from the list generated by the `tag_sentences` method
            alignment {list} -- List of tuples with the alignment between the setences
            tw_size {int} -- Window size for the computation of the features
            target {str} -- Error corresponding to the sentence,
                            if the translation is correct this parameter must be valued to `correct`

        Returns:
            dict -- Dictionary with all features to the sentence pair
        """
        tagged_src = tagged_sent[0]
        tagged_sys = tagged_sent[1]

        lct_src_index = list()
        lct_sys_index = list()

        # Apertium deals with MWE
        # Indices where one has MWE
        has_mw_src = [(i, w[0].count(' '))
                      for (i, w) in enumerate(tagged_src) if ' ' in w[0]]
        has_mw_sys = [(i, w[0].count(' '))
                      for (i, w) in enumerate(tagged_sys) if ' ' in w[0]]

        # Get LCT
        if target == 'correct':
            while not lct_sys_index or None in lct_sys_index:
                lct_src_index = random.choice(range(len(tagged_src)))
                # Get sys LCT by alignment
                lct_sys_index = [a[1]
                                 for a in alignment if a[0] == lct_src_index]

            # Correct alignment of tokens in case of MWE
            if has_mw_src:
                for (i, num_spaces) in has_mw_src:
                    lct_src_index = [lct if lct <= i else lct -
                                     min(num_spaces, lct - i) for lct in [lct_src_index]][0]
            if has_mw_sys:
                for (i, num_spaces) in has_mw_sys:
                    lct_sys_index = [lct if lct <= i else lct -
                                     min(num_spaces, lct - i) for lct in lct_sys_index]

            if len(lct_sys_index) < 3:
                lct_sys_index = lct_sys_index[0]
            else:
                lct_sys_index = lct_sys_index[len(lct_sys_index) // 2]
        else:
            lct_src_index = target[0]
            lct_sys_index = target[1]

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

        for i in range(tw_size):
            try:
                tok = sys_tw[i]
            except IndexError:
                tok = list()
            finally:
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
        features['sysBegCap'] = True if tagged_sys[lct_sys_index][0][0].isupper(
        ) else False

        # Features sys and src
        for i in range(tw_size):
            try:
                tok = src_tw[i]
            except IndexError:
                tok = list()
            finally:
                key = ''
                tok_tags = re.sub(r'_\+[^_$]+_', '+', '_'.join(tok[1:]))
                if i < tw_size // 2:
                    key = 'posToken{}BefSrc'.format(i + 1)
                elif i == tw_size // 2:
                    key = 'posSrcToken'
                else:
                    key = 'posToken{}AftSrc'.format(i - (tw_size // 2))
                features[key] = tok_tags if tok_tags else 'NC'

        for i in range(tw_size):
            try:
                tok = sys_tw[i]
            except:
                tok = list()
            finally:
                key = ''
                tok_tags = re.sub(r'_\+[^_$]+_', '+', '_'.join(tok[1:]))
                if i < tw_size // 2:
                    key = 'posToken{}BefSys'.format(i + 1)
                elif i == tw_size // 2:
                    key = 'posSysToken'
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

        features['srcSysVRatio'] = max(
            num_verbs_src, 1) / max(num_verbs_sys, 1)
        features['srcSysNRatio'] = max(
            num_nouns_src, 1) / max(num_nouns_sys, 1)

        # Remove * from start of lct if exists
        flat_lct_src = re.sub(r'\*', '', tagged_src[lct_src_index][0])
        flat_lct_sys = re.sub(r'\*', '', tagged_sys[lct_sys_index][0])

        features['equalTokenSrcSys'] = flat_lct_src == flat_lct_sys
        special_char_src = flat_lct_src in string.punctuation or 'num' in tagged_src[
            lct_src_index]
        special_char_sys = flat_lct_sys in string.punctuation or 'num' in tagged_sys[
            lct_sys_index]
        features['specialCharSrcSys'] = special_char_src and special_char_sys

        # Include target to the features dictionary
        features['target'] = target

        return features
