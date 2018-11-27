import argparse
import numpy
from readers.read_blast import BlastReader

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--test', '-t',
                        help='Caminho para arquivo BLAST de teste',
                        required=True)
arg_parser.add_argument('--ref', '-r',
                        help='Caminho para arquivo BLAST de referencia',
                        required=True)
arg_parser.add_argument('--limit', '-l',
                        help='Limite de sentencas para processamento',
                        type=int,
                        required=False)
ARGS = arg_parser.parse_args()


BLAST_PATH_TEST = ARGS.test
BLAST_PATH_REF = ARGS.ref
SENT_LIMIT = ARGS.limit
TIPO_ERROS = ['lex-incTrWord', 'lex-notTrWord']


def calcula_medidas():
    blast_reader_test = BlastReader(BLAST_PATH_TEST)
    blast_reader_ref = BlastReader(BLAST_PATH_REF)

    verdadeiro_positivo = 0
    falso_positivo = 0
    for (sent_idx_test, error) in blast_reader_test.error_lines:
        if SENT_LIMIT is None or (SENT_LIMIT is not None and sent_idx_test < SENT_LIMIT):
            error_type = error[-1]
            sys_idxs = error[1]

            fp = 1
            for (sent_idx_ref, error2) in blast_reader_ref.get_filtered_errors([error_type]):
                if sent_idx_ref == sent_idx_test:
                    if set(sys_idxs) & set(error2[1]):
                        verdadeiro_positivo += 1
                        fp = 0
                        break
            falso_positivo += fp

    falso_negativo = 0
    for (idx, error) in blast_reader_ref.error_lines:
        if SENT_LIMIT is None or (SENT_LIMIT is not None and sent_idx_test < SENT_LIMIT):
            error_type = error[-1]
            sys_idxs = error[1]

            fn = 1
            for (idx2, error2) in blast_reader_test.get_filtered_errors([error_type]):
                if idx2 == idx:
                    if set(sys_idxs) & set(error2[1]):
                        fn = 0
                        break
            falso_negativo += fn

    precisao = verdadeiro_positivo / (verdadeiro_positivo + falso_positivo)
    cobertura = verdadeiro_positivo / (verdadeiro_positivo + falso_negativo)

    print('Precisao: {:.2f}%'.format(precisao*100))
    print('Cobertura: {:.2f}%'.format(cobertura*100))


def calcula_matriz_confusao():
    blast_reader_test = BlastReader(BLAST_PATH_TEST)
    blast_reader_ref = BlastReader(BLAST_PATH_REF)

    indices_matriz = {x: TIPO_ERROS.index(x) for x in TIPO_ERROS}
    indices_matriz['correto'] = len(indices_matriz)

    matriz = numpy.zeros((len(TIPO_ERROS) + 1, len(TIPO_ERROS) + 1))

    for (sent_idx_test, sent) in enumerate(blast_reader_test.sys_lines):
        if SENT_LIMIT is None or (SENT_LIMIT is not None and sent_idx_test < SENT_LIMIT):
            sent_class = blast_reader_test.get_error_messages(sent_idx_test)
            sent_class_ref = blast_reader_ref.get_error_messages(sent_idx_test)

            for (palavra_idx, palavra) in enumerate(sent):
                # Classificacao
                palavra_erros = [x for x in sent_class if palavra_idx in x[1]]
                if palavra_erros:
                    idx_linha = indices_matriz[palavra_erros[0][-1]]
                else:
                    idx_linha = indices_matriz['correto']

                # Referencia
                palavra_ref = [x for x in sent_class_ref if palavra_idx in x[1] and x[-1] in TIPO_ERROS]
                if palavra_ref:
                    idx_coluna = indices_matriz[palavra_ref[0][-1]]
                else:
                    idx_coluna = indices_matriz['correto']

                matriz[idx_linha, idx_coluna] += 1
    print(indices_matriz)
    matprint(matriz)


def matprint(mat, fmt="g"):
    col_maxes = [max([len(("{:"+fmt+"}").format(x)) for x in col]) for col in mat.T]
    for x in mat:
        for i, y in enumerate(x):
            print(("{:"+str(col_maxes[i])+fmt+"}").format(y), end="  ")
        print("")


if __name__ == "__main__":
    calcula_medidas()
    print('\n------------------------\n')
    calcula_matriz_confusao()
