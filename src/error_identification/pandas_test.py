import pandas as pd
import numpy as np
import pickle
import re
import sys

a = None

with open('../../features.pkl', 'rb') as _file:
    a = pickle.load(_file)

b = pd.DataFrame(a, columns=a[0].keys())

string_cols = b.select_dtypes(include='object')
b = b.select_dtypes(exclude='object')

for col in string_cols:
    nova_coluna = pd.get_dummies(string_cols[col].str.split('_').apply(
        pd.Series).stack(), prefix=col, prefix_sep='_').sum(level=0)
    b = b.join(nova_coluna)

with open('features_csv.txt', 'w') as _file:
    b.to_csv(_file)

# coluna_antiga = b['posToken2BefSrc'].str.split('_').apply(pd.Series).stack()
# print(pd.get_dummies(coluna_antiga).sum(level=0))
