#!/usr/bin/env python3
import numpy as np
from sklearn.model_selection import KFold
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC
from sklearn.linear_model import Perceptron
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.metrics import classification_report
from sklearn.base import clone
from readers.read_blast import BlastReader
from readers.read_giza import GIZAReader
from utils import *

# BLAST_PATH = '/home/marciolima/Documentos/Lalic/post-editing/src/error_identification/error-ident-blast.txt'
# BLAST_PATH = '/home/marciolima/Documentos/Lalic/post-editing/src/error_identification/exemplo.blast'
BLAST_PATH = '/home/marciolima/Documentos/WE-PE-tool/error-ident-blast.txt'
FEATURES_FILE = 'features_final.pkl'
TW_SZ = 5
ERRORS = ['lex-incTrWord', 'lex-notTrWord']

lb_step1 = LabelEncoder()
lb_step2 = LabelEncoder()


def test_two_steps(data, model):
    X = data.loc[:, data.columns != 'target']
    y = data['target']

    kf = KFold(n_splits=10, shuffle=True)
    num_fold = 0
    for (train, test) in kf.split(X):
        num_fold += 1
        print('Fold {}'.format(num_fold))

        X_step1_train = X.loc[train]
        y_step1_train = y.loc[train]
        y_step1_train.loc[y_step1_train != 'correct'] = 'error'
        y_step1_train = lb_step1.fit_transform(y_step1_train)
        print('Classes: {}'.format(lb_step1.classes_))

        model_step1 = clone(model)
        model_step1.fit(X_step1_train, y_step1_train)

        X_step2_train = X.loc[train]
        y_step2_train = y.loc[train]
        X_step2_train = X_step2_train[y.loc[train] != 'correct']
        y_step2_train = y_step2_train[y.loc[train] != 'correct']
        lb_step2.fit(y)
        print('Classes: {}'.format(lb_step2.classes_))
        y_step2_train = lb_step2.transform(y_step2_train)

        model_step2 = model
        model_step2.fit(X_step2_train, y_step2_train)

        X_test = X.loc[test]
        y_step1_test = y.loc[test]
        y_step2_test = y.loc[test]

        results_step1 = model_step1.predict(X_test)
        y_step1_test.loc[y_step1_test != 'correct'] = 'error'
        y_step1_test = lb_step1.transform(y_step1_test)
        print(classification_report(y_step1_test, results_step1))

        error_lb = lb_step1.transform(['error'])[0]
        X_step2_test = X_test[results_step1 == error_lb]

        results_step2 = model_step2.predict(X_step2_test)
        y_step2_test = y_step2_test[results_step1 == error_lb]
        y_step2_test = lb_step2.transform(y_step2_test)
        print(classification_report(y_step2_test, results_step2))

        y_final_pred = results_step1[results_step1 != error_lb]
        y_final_pred = np.hstack((y_final_pred, results_step2))

        y_final_true = y_step1_test[results_step1 != error_lb]
        y_final_true = np.hstack((y_final_true, y_step2_test))

        print(classification_report(y_final_true, y_final_pred))

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

    print('Arvore de Decisao - GINI')
    test_two_steps(data, DecisionTreeClassifier())
    print('------------------------')
    print('Arvore de Decisao - Entropy')
    test_two_steps(data, DecisionTreeClassifier(criterion='entropy'))
    print('------------------------')
    print('SVM')
    test_two_steps(data, LinearSVC())
    print('------------------------')
    print('SVM - Crammer-Singer')
    test_two_steps(data, LinearSVC(multi_class='crammer_singer'))
    print('------------------------')
    print('Perceptron')
    test_two_steps(data, Perceptron(n_jobs=-1))
    print('------------------------')
    print('Random Forest - GINI')
    test_two_steps(data, RandomForestClassifier(n_estimators=10))
    print('------------------------')
    print('Random Forest - Entropy')
    test_two_steps(data, RandomForestClassifier(n_estimators=10, criterion='entropy'))
    print('------------------------')
    print('Naive Bayes')
    test_two_steps(data, BernoulliNB())
    print('------------------------')


if __name__ == '__main__':
    main()
