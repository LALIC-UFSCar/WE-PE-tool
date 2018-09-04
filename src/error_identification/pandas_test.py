import pickle
import re
import sys
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier

a = None

with open('../../features4.pkl', 'rb') as _file:
    a = pickle.load(_file)

features = list(a[0].keys())
features.remove('target')
b = pd.DataFrame(a, columns=features)

# Get in DataFrame only numeric and boolean columns
string_cols = b.select_dtypes(include='object')
b = b.select_dtypes(exclude='object')

# For each column with string features
# Split with '_' and code with get_dummies
for col in string_cols:
    nova_coluna = pd.get_dummies(string_cols[col].str.split('_').apply(
        pd.Series).stack(), prefix=col, prefix_sep='_').sum(level=0)
    b = b.join(nova_coluna)

# Add target column
b = b.join(pd.DataFrame(a, columns=['target']))

# Get only error label in the target column
error_cols = b.loc[b['target'] != 'correct', 'target']
error_cols = error_cols.apply(pd.Series)[3]
b.loc[b['target'] != 'correct', 'target'] = error_cols

# Replace not correct targets with error
b.loc[b['target'] != 'correct', 'target'] = 'error'

print(b)
