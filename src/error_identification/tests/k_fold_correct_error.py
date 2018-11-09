#!/usr/bin/env python3
import subprocess
import os
import progressbar
import sys
from readers.read_blast import BlastReader
from readers.read_giza import GIZAReader
from utils import tag_sentences, extract_features, format_features
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import KFold
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC
from sklearn.linear_model import Perceptron
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report, recall_score, make_scorer

# BLAST_PATH = '/home/marciolima/Documentos/Lalic/post-editing/src/error_identification/error-ident-blast.txt'
# BLAST_PATH = '/home/marciolima/Documentos/Lalic/post-editing/src/error_identification/exemplo.blast'
BLAST_PATH = '/home/marciolima/Documentos/WE-PE-tool/error-ident-blast.txt'
FEATURES_FILE = 'features_final.pkl'
TW_SZ = 5
ERRORS = ['lex-incTrWord', 'lex-notTrWord']

lb = LabelEncoder()

def test_correct_error(data):
    # Replace not correct targets with error
    data.loc[data['target'] != 'correct', 'target'] = 'error'
    # Encode target into numbers
    data['target'] = lb.fit_transform(data['target'])

    X = data.loc[:, data.columns != 'target']
    y = data['target']

    kf = KFold(n_splits=10, shuffle=True)

    print('Arvore de decisao')
    avg_precision = 0
    avg_precision_correct = 0
    avg_precision_error = 0
    fold = 1
    for (train, test) in kf.split(X):
        # Training
        dt = DecisionTreeClassifier()
        dt.fit(X.loc[train], y.loc[train])

        results = dt.predict(X.loc[test])
        precision = accuracy_score(y.loc[test], results)
        avg_precision += precision

        precision_correct = accuracy_score(
            y.loc[test].loc[y.loc[test] == 0], results[y.loc[test] == lb.transform(['correct'])[0]])
        avg_precision_correct += precision_correct
        precision_error = accuracy_score(
            y.loc[test].loc[y.loc[test] != 0], results[y.loc[test] != lb.transform(['correct'])[0]])
        avg_precision_error += precision_error

        print('Precisao - Fold {}: {:.2f}%'.format(fold, precision * 100))
        print('Precisao corretas - Fold {}: {:.2f}%'.format(fold,
                                                            precision_correct * 100))
        print('Precisao erros - Fold {}: {:.2f}%\n'.format(fold, precision_error * 100))
        fold += 1
    avg_precision /= 10
    avg_precision_correct /= 10
    avg_precision_error /= 10
    print('Precisao media: {:.2f}%'.format(avg_precision * 100))
    print('Precisao media corretas: {:.2f}%'.format(
        avg_precision_correct * 100))
    print('Precisao media erros: {:.2f}%'.format(avg_precision_error * 100))
    print('------------------------------')

    print('SVM')
    avg_precision = 0
    avg_precision_correct = 0
    avg_precision_error = 0
    fold = 1
    for (train, test) in kf.split(X):
        svm = LinearSVC()
        svm.fit(X.loc[train], y.loc[train])

        results = svm.predict(X.loc[test])
        precision = accuracy_score(y.loc[test], results)
        avg_precision += precision

        precision_correct = accuracy_score(
            y.loc[test].loc[y.loc[test] == 0], results[y.loc[test] == lb.transform(['correct'])[0]])
        avg_precision_correct += precision_correct
        precision_error = accuracy_score(
            y.loc[test].loc[y.loc[test] != 0], results[y.loc[test] != lb.transform(['correct'])[0]])
        avg_precision_error += precision_error

        print('Precisao - Fold {}: {:.2f}%'.format(fold, precision * 100))
        print('Precisao corretas - Fold {}: {:.2f}%'.format(fold,
                                                            precision_correct * 100))
        print('Precisao erros - Fold {}: {:.2f}%\n'.format(fold, precision_error * 100))
        fold += 1
    avg_precision /= 10
    avg_precision_correct /= 10
    avg_precision_error /= 10
    print('Precisao media: {:.2f}%'.format(avg_precision * 100))
    print('Precisao media corretas: {:.2f}%'.format(
        avg_precision_correct * 100))
    print('Precisao media erros: {:.2f}%'.format(avg_precision_error * 100))
    print('------------------------------')

    print('Perceptron')
    avg_precision = 0
    avg_precision_correct = 0
    avg_precision_error = 0
    fold = 1
    for (train, test) in kf.split(X):
        perceptron = Perceptron()
        perceptron.fit(X.loc[train], y.loc[train])

        results = perceptron.predict(X.loc[test])
        precision = accuracy_score(y.loc[test], results)
        avg_precision += precision

        precision_correct = accuracy_score(
            y.loc[test].loc[y.loc[test] == 0], results[y.loc[test] == lb.transform(['correct'])[0]])
        avg_precision_correct += precision_correct
        precision_error = accuracy_score(
            y.loc[test].loc[y.loc[test] != 0], results[y.loc[test] != lb.transform(['correct'])[0]])
        avg_precision_error += precision_error

        print('Precisao - Fold {}: {:.2f}%'.format(fold, precision * 100))
        print('Precisao corretas - Fold {}: {:.2f}%'.format(fold,
                                                            precision_correct * 100))
        print('Precisao erros - Fold {}: {:.2f}%\n'.format(fold, precision_error * 100))
        fold += 1
    avg_precision /= 10
    avg_precision_correct /= 10
    avg_precision_error /= 10
    print('Precisao media: {:.2f}%'.format(avg_precision * 100))
    print('Precisao media corretas: {:.2f}%'.format(
        avg_precision_correct * 100))
    print('Precisao media erros: {:.2f}%'.format(avg_precision_error * 100))
    print('------------------------------')

    print('Random Forest')
    avg_precision = 0
    avg_precision_correct = 0
    avg_precision_error = 0
    fold = 1
    for (train, test) in kf.split(X):
        random_forest = RandomForestClassifier()
        random_forest.fit(X.loc[train], y.loc[train])

        results = random_forest.predict(X.loc[test])
        precision = accuracy_score(y.loc[test], results)
        avg_precision += precision

        precision_correct = accuracy_score(
            y.loc[test].loc[y.loc[test] == 0], results[y.loc[test] == lb.transform(['correct'])[0]])
        avg_precision_correct += precision_correct
        precision_error = accuracy_score(
            y.loc[test].loc[y.loc[test] != 0], results[y.loc[test] != lb.transform(['correct'])[0]])
        avg_precision_error += precision_error

        print('Precisao - Fold {}: {:.2f}%'.format(fold, precision * 100))
        print('Precisao corretas - Fold {}: {:.2f}%'.format(fold,
                                                            precision_correct * 100))
        print('Precisao erros - Fold {}: {:.2f}%\n'.format(fold, precision_error * 100))
        fold += 1
    avg_precision /= 10
    avg_precision_correct /= 10
    avg_precision_error /= 10
    print('Precisao media: {:.2f}%'.format(avg_precision * 100))
    print('Precisao media corretas: {:.2f}%'.format(
        avg_precision_correct * 100))
    print('Precisao media erros: {:.2f}%'.format(avg_precision_error * 100))
    print('------------------------------')

    print('Naive Bayes')
    avg_precision = 0
    avg_precision_correct = 0
    avg_precision_error = 0
    fold = 1
    for (train, test) in kf.split(X):
        naive_bayes = GaussianNB()
        naive_bayes.fit(X.loc[train], y.loc[train])

        results = naive_bayes.predict(X.loc[test])
        precision = accuracy_score(y.loc[test], results)
        avg_precision += precision

        precision_correct = accuracy_score(
            y.loc[test].loc[y.loc[test] == 0], results[y.loc[test] == lb.transform(['correct'])[0]])
        avg_precision_correct += precision_correct
        precision_error = accuracy_score(
            y.loc[test].loc[y.loc[test] != 0], results[y.loc[test] != lb.transform(['correct'])[0]])
        avg_precision_error += precision_error

        print('Precisao - Fold {}: {:.2f}%'.format(fold, precision * 100))
        print('Precisao corretas - Fold {}: {:.2f}%'.format(fold,
                                                            precision_correct * 100))
        print('Precisao erros - Fold {}: {:.2f}%\n'.format(fold, precision_error * 100))
        fold += 1
    avg_precision /= 10
    avg_precision_correct /= 10
    avg_precision_error /= 10
    print('Precisao media: {:.2f}%'.format(avg_precision * 100))
    print('Precisao media corretas: {:.2f}%'.format(
        avg_precision_correct * 100))
    print('Precisao media erros: {:.2f}%'.format(avg_precision_error * 100))


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
    print('Tagging sentences', file=sys.stderr)
    tagged_lines = tag_sentences(src_lines, sys_lines)

    # Align sentences
    print('Aligning sentences', file=sys.stderr)
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
    print('Extracting features', file=sys.stderr)
    training_instances = list()
    ignored_instances = 0
    for (i, sent) in progressbar.progressbar(enumerate(tagged_lines)):
        features = extract_features(
            sent, alignments[i]['alignment'], TW_SZ, target[i])
        if features:
            training_instances.append(features)
        else:
            ignored_instances += 1
    print('Finalizado!', file=sys.stderr)
    print('Instancias ignoradas: {}'.format(ignored_instances), file=sys.stderr)

    print('Iniciando treinamento', file=sys.stderr)
    data = format_features(training_instances)
    test_correct_error(data)


if __name__ == '__main__':
    main()
