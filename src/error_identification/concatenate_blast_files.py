#!/usr/bin/env python3
from readers.read_blast import BlastReader

NMT_PATH = '/home/marciolima/Documentos/Lalic/post-editing/src/error_identification/error-ident-NMT.txt'
PBSMT_PATH = '/home/marciolima/Documentos/Lalic/post-editing/src/error_identification/error-ident-PBSMT.txt'

nmt_br = BlastReader(NMT_PATH)

with open('error-ident-blast.txt', 'a') as _file:
    # Just copy PBSMT file
    with open(PBSMT_PATH) as pbsmt_file:
        for line in pbsmt_file:
            _file.write(line)

    # Get 300 first sentences from NMT file
    for i in range(300):
        _file.write(' '.join(nmt_br.src_lines[i]))
        _file.write('\n')
        _file.write(' '.join(nmt_br.ref_lines[i]))
        _file.write('\n')
        _file.write(' '.join(nmt_br.sys_lines[i]))
        _file.write('\n\n')

        error_message = ''
        for error in nmt_br.get_error_messages(i):
            error_indices = [','.join(str(idx) for idx in indices)
                             for indices in error[:-1]]
            error_indices.append(error[-1])
            error_message += '#'.join(error_indices)
            error_message += ' '

        _file.write(error_message)
        _file.write('\n')
