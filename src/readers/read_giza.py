import re


class GIZAReader(object):
    def __init__(self, filename):
        self.aligned_lines = list()
        with open(filename, 'r') as giza_file:
            while True:
                line_info = giza_file.readline()
                if not line_info:
                    break
                line_plain = giza_file.readline()
                line_aligned = giza_file.readline()

                line_num = int(re.findall(r'\(([^\)]*)\)', line_info)[0])
                line_aligned = re.findall(
                    r'([^\(]+) \(\{([^\}]*)\}\)', line_aligned)
                alignment = list()

                for (i, w) in enumerate(line_aligned):
                    indices = map(int, w[1].split())
                    if not indices:
                        alignment.append((i - 1, None))
                    else:
                        alignment.extend(
                            [(None, j - 1) if w[0] == 'NULL' else (i - 1, j - 1) for j in indices])

                self.aligned_lines.append({'num': line_num - 1,
                                           'sys': line_plain.split(),
                                           'src': [w[0] for w in line_aligned if w[0] != 'NULL'],
                                           'alignment': alignment})
        self.aligned_lines = sorted(self.aligned_lines, key=lambda x: x['num'])
