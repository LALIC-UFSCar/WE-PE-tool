#!/usr/bin/env python3
import subprocess
import os
import progressbar
import sys
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import cross_validate
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC
from sklearn.linear_model import Perceptron
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.metrics import classification_report, recall_score, make_scorer
from readers.read_blast import BlastReader
from readers.read_giza import GIZAReader
from utils import extract_features, format_features, tag_sentences

# BLAST_PATH = '/home/marciolima/Documentos/Lalic/post-editing/src/error_identification/error-ident-blast.txt'
# BLAST_PATH = '/home/marciolima/Documentos/Lalic/post-editing/src/error_identification/exemplo.blast'
BLAST_PATH = '/home/marciolima/Documentos/WE-PE-tool/error-ident-blast.txt'
FEATURES_FILE = 'features_final.pkl'
TW_SZ = 5
ERRORS = ['lex-incTrWord', 'lex-notTrWord']

lb = LabelEncoder()


def multiclass_recall(y, y_pred, **kwargs):
    print(classification_report(y, y_pred))
    return recall_score(y, y_pred, average='weighted')


def test_multiclass(data):
    data['target'] = lb.fit_transform(data['target'])
    print('Classes: {}'.format(list(lb.classes_)))

    X = data.loc[:, data.columns != 'target']
    y = data['target']

    print('Arvore de decisao - GINI')
    dt = DecisionTreeClassifier()
    scores = cross_validate(dt, X, y=y, cv=10, scoring={
                            'acc': 'accuracy', 'rec': make_scorer(multiclass_recall), 'f1': 'f1_weighted'}, return_train_score=False)

    print('Acurácia: {:.2f} (+/- {:.2f})'.format(
        scores['test_acc'].mean(), scores['test_acc'].std()))
    print('Cobertura: {:.2f} (+/- {:.2f})'.format(
        scores['test_rec'].mean(), scores['test_rec'].std()))
    print(
        'F-score: {:.2f} (+/- {:.2f})'.format(scores['test_f1'].mean(), scores['test_f1'].std()))
    print('------------------------------')

    print('Arvore de decisao - Entropy')
    dt = DecisionTreeClassifier(criterion='entropy')
    scores = cross_validate(dt, X, y=y, cv=10, scoring={
                            'acc': 'accuracy', 'rec': make_scorer(multiclass_recall), 'f1': 'f1_weighted'}, return_train_score=False)

    print('Acurácia: {:.2f} (+/- {:.2f})'.format(
        scores['test_acc'].mean(), scores['test_acc'].std()))
    print('Cobertura: {:.2f} (+/- {:.2f})'.format(
        scores['test_rec'].mean(), scores['test_rec'].std()))
    print(
        'F-score: {:.2f} (+/- {:.2f})'.format(scores['test_f1'].mean(), scores['test_f1'].std()))
    print('------------------------------')

    print('SVM - Um contra todos')
    dt = LinearSVC()
    scores = cross_validate(dt, X, y=y, cv=10, scoring={
                            'acc': 'accuracy', 'rec': make_scorer(multiclass_recall), 'f1': 'f1_weighted'}, return_train_score=False)

    print('Acurácia: {:.2f} (+/- {:.2f})'.format(
        scores['test_acc'].mean(), scores['test_acc'].std()))
    print('Cobertura: {:.2f} (+/- {:.2f})'.format(
        scores['test_rec'].mean(), scores['test_rec'].std()))
    print(
        'F-score: {:.2f} (+/- {:.2f})'.format(scores['test_f1'].mean(), scores['test_f1'].std()))
    print('------------------------------')

    print('SVM - Crammer-Singer')
    dt = LinearSVC(multi_class='crammer_singer')
    scores = cross_validate(dt, X, y=y, cv=10, scoring={
                            'acc': 'accuracy', 'rec': make_scorer(multiclass_recall), 'f1': 'f1_weighted'}, return_train_score=False)

    print('Acurácia: {:.2f} (+/- {:.2f})'.format(
        scores['test_acc'].mean(), scores['test_acc'].std()))
    print('Cobertura: {:.2f} (+/- {:.2f})'.format(
        scores['test_rec'].mean(), scores['test_rec'].std()))
    print(
        'F-score: {:.2f} (+/- {:.2f})'.format(scores['test_f1'].mean(), scores['test_f1'].std()))
    print('------------------------------')

    print('Perceptron')
    dt = Perceptron()
    scores = cross_validate(dt, X, y=y, cv=10, scoring={
                            'acc': 'accuracy', 'rec': make_scorer(multiclass_recall), 'f1': 'f1_weighted'}, return_train_score=False)

    print('Acurácia: {:.2f} (+/- {:.2f})'.format(
        scores['test_acc'].mean(), scores['test_acc'].std()))
    print('Cobertura: {:.2f} (+/- {:.2f})'.format(
        scores['test_rec'].mean(), scores['test_rec'].std()))
    print(
        'F-score: {:.2f} (+/- {:.2f})'.format(scores['test_f1'].mean(), scores['test_f1'].std()))
    print('------------------------------')

    print('Random Forest - GINI')
    dt = RandomForestClassifier()
    scores = cross_validate(dt, X, y=y, cv=10, scoring={
                            'acc': 'accuracy', 'rec': make_scorer(multiclass_recall), 'f1': 'f1_weighted'}, return_train_score=False)

    print('Acurácia: {:.2f} (+/- {:.2f})'.format(
        scores['test_acc'].mean(), scores['test_acc'].std()))
    print('Cobertura: {:.2f} (+/- {:.2f})'.format(
        scores['test_rec'].mean(), scores['test_rec'].std()))
    print(
        'F-score: {:.2f} (+/- {:.2f})'.format(scores['test_f1'].mean(), scores['test_f1'].std()))
    print('------------------------------')

    print('Random Forest - Entropy')
    dt = RandomForestClassifier(criterion='entropy')
    scores = cross_validate(dt, X, y=y, cv=10, scoring={
                            'acc': 'accuracy', 'rec': make_scorer(multiclass_recall), 'f1': 'f1_weighted'}, return_train_score=False)

    print('Acurácia: {:.2f} (+/- {:.2f})'.format(
        scores['test_acc'].mean(), scores['test_acc'].std()))
    print('Cobertura: {:.2f} (+/- {:.2f})'.format(
        scores['test_rec'].mean(), scores['test_rec'].std()))
    print(
        'F-score: {:.2f} (+/- {:.2f})'.format(scores['test_f1'].mean(), scores['test_f1'].std()))
    print('------------------------------')

    print('Naive Bayes')
    dt = BernoulliNB()
    scores = cross_validate(dt, X, y=y, cv=10, scoring={
                            'acc': 'accuracy', 'rec': make_scorer(multiclass_recall), 'f1': 'f1_weighted'}, return_train_score=False)

    print('Acurácia: {:.2f} (+/- {:.2f})'.format(
        scores['test_acc'].mean(), scores['test_acc'].std()))
    print('Cobertura: {:.2f} (+/- {:.2f})'.format(
        scores['test_rec'].mean(), scores['test_rec'].std()))
    print(
        'F-score: {:.2f} (+/- {:.2f})'.format(scores['test_f1'].mean(), scores['test_f1'].std()))


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
    test_multiclass(data)


if __name__ == '__main__':
    main()
