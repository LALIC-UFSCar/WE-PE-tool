#!/usr/bin/env python3
from sklearn.preprocessing import LabelEncoder
from readers.read_blast import BlastReader
from readers.read_giza import GIZAReader
from utils import *

# BLAST_PATH = '/home/marciolima/Documentos/Lalic/post-editing/src/error_identification/error-ident-blast.txt'
# BLAST_PATH = '/home/marciolima/Documentos/Lalic/post-editing/src/error_identification/exemplo.blast'
BLAST_PATH = '/home/marciolima/Documentos/WE-PE-tool/error-ident-blast.txt'
FEATURES_FILE = 'features_final.pkl'
TW_SZ = 5
ERRORS = ['lex-incTrWord', 'lex-notTrWord']

lb = LabelEncoder()

def test_two_steps(data):
    data['target'] = lb.fit_transform(data['target'])

    data_step1 = data
    data_step1.loc[data_step1['target'] != 'correct', 'target'] = 'error'
    data_step1['target'] = lb.transform(data_step1['target'])

    X_step1 = data_step1.loc[:, data.columns != 'target']
    y_step1 = data_step1['target']

    print(X_step1)


def main():
    """Main function
    """
    blast_reader = BlastReader(BLAST_PATH)
    src_lines = list()
    sys_lines = list()
    target = list()

    # Files for GIZA
    src_file = open('/tmp/src.txt', 'w')
    sys_file = open('/tmp/sys.txt', 'w')

    # Correct sentences
    for i in blast_reader.get_correct_indices():
        src_lines.append(blast_reader.src_lines[i])
        sys_lines.append(blast_reader.sys_lines[i])
        target.append('correct')

        # Write files for GIZA
        src_file.write(' '.join(blast_reader.src_lines[i]))
        src_file.write('\n')
        sys_file.write(' '.join(blast_reader.sys_lines[i]))
        sys_file.write('\n')

    # Error lines
    errors = blast_reader.get_filtered_errors(ERRORS)
    # errors = blast_reader.error_lines
    for (line, error) in errors:
        src_lines.append(blast_reader.src_lines[line])
        sys_lines.append(blast_reader.sys_lines[line])
        target.append(error)

        src_file.write(' '.join(blast_reader.src_lines[line]))
        src_file.write('\n')
        sys_file.write(' '.join(blast_reader.sys_lines[line]))
        sys_file.write('\n')
    src_file.close()
    sys_file.close()

    # Tag sentences
    print('Tagging sentences')
    tagged_lines = tag_sentences(src_lines, sys_lines)

    # Align sentences
    print('Aligning sentences')
    application_path = str(os.path.abspath(os.path.curdir))
    proc = subprocess.Popen([application_path + '/src/aligner/align_sentences.sh',
                             '--srcpath', '/tmp/src.txt',
                             '--syspath', '/tmp/sys.txt'],
                            stdout=subprocess.PIPE)
    out = proc.communicate()
    num_sents = int(out[0])
    giza_reader = GIZAReader('/tmp/giza.output')
    alignments = giza_reader.aligned_lines[:num_sents]

    # Extract features
    print('Extracting features')
    training_instances = list()
    ignored_instances = 0
    for (i, sent) in progressbar.progressbar(enumerate(tagged_lines)):
        features = extract_features(
            sent, alignments[i]['alignment'], TW_SZ, target[i])
        if features:
            training_instances.append(features)
        else:
            ignored_instances += 1
    print('Finalizado!')
    print('Instancias ignoradas: {}'.format(ignored_instances))

    print('Iniciando treinamento')
    data = format_features(training_instances)
    test_two_steps(data)


if __name__ == '__main__':
    main()
