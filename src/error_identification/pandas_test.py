import pickle
import re
import sys
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn import model_selection
from sklearn.metrics import accuracy_score

a = None

with open('/home/marcio/SHARED/SHARED/Lalic/post-editing/src/error_identification/features4.pkl', 'rb') as _file:
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

# Encode target into numbers
lb = LabelEncoder()
b['target'] = lb.fit_transform(b['target'])

# Get train instance values
X = b.loc[:, b.columns != 'target']
y = b['target']

kf = model_selection.KFold(n_splits=10, shuffle=True)

for (train, test) in kf.split(X):
    # Training
    dt = DecisionTreeClassifier()
    dt.fit(X.loc[train], y.loc[train])

    results = dt.predict(X.loc[test])
    print('Precisao: {}'.format(accuracy_score(y.loc[test], results)))
