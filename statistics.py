#!/usr/bin/env python3
import sys
from readers.read_ape import ApeReader

FILE_PATH = sys.argv[1]

ape_reader = ApeReader(FILE_PATH)

print('Ocorrencias do erro: {}'.format(len(ape_reader.error_lines)))

cores = list()
for k in ape_reader.corrections:
    flat = [sub[1] for sub in k]
    cores.append(flat)

print('Nenhuma sugestao de correcao: {}'.format(
    len([x for x in cores if len(x) < 2])))

print('Efetivamente avaliadas: {}'.format(
    len([x for x in cores if 'red' in x or 'green' in x or 'yellow' in x])))

print('Pelo menos uma sugestao correta: {}'.format(
    len([x for x in cores if 'green' in x])))

print('Pelo menos uma sugestao parcialmente correta: {}'.format(
    len([x for x in cores if 'yellow' in x])))

print('Pelo menos uma sugestao parcialmente correta e nenhuma correta: {}'.format(
    len([x for x in cores if 'yellow' in x and 'green' not in x])))

print('Pelo menos uma sugestao errada: {}'.format(
    len([x for x in cores if 'red' in x])))

print('Todas as sugestoes erradas: {}'.format(
    len([x for x in cores if 'red' in x and 'green' not in x and 'yellow' not in x])))
