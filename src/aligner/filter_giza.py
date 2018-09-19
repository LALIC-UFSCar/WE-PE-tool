#!/usr/bin/env python3
import argparse
import re
from itertools import islice

parser = argparse.ArgumentParser()
parser.add_argument('--filepath', '-f', required=True,
                    help='Path to the GIZA++ output file',
                    type=str)
parser.add_argument('--numlines', '-n', required=True,
                    help='Number of lines to retrieve from the file',
                    type=int)

FLAGS = parser.parse_args()

aligned_lines = list()
with open(FLAGS.filepath, 'r') as giza_file:
    while True:
        line_info = giza_file.readline()
        if not line_info:
            break
        line_plain = giza_file.readline()
        line_aligned = giza_file.readline()

        line_num = int(re.findall(r'\(([^\)]*)\)', line_info)[0])
        if line_num <= FLAGS.numlines:
            line_aligned = re.findall(r'(\w+) \(\{([^\}]*)\}\)', line_aligned)
            alignment = list()

            for (i, w) in enumerate(line_aligned):
                indices = map(int, w[1].split())
                alignment.extend(
                    [(j - 1, None) if w[0] == 'NULL' else (j - 1, i - 1) for j in indices])

            aligned_lines.append({'num': line_num,
                                  'lang1': line_plain.split(),
                                  'lang2': [w[0] for w in line_aligned if w[0] != 'NULL'],
                                  'alignment': alignment})

print(aligned_lines[0]['lang1'])
print(aligned_lines[0]['lang2'])
print(aligned_lines[0]['alignment'])
