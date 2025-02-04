import numpy as np
from itertools import product
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC
from sklearn.datasets import load_iris
param_grid = {
    'SVC': {'C': [0.1, 1, 10],
            'kernel': ['linear', 'rbf']}
}
def gridsearch(X,y,param_grid,k_folds):
    dico={}
    for keys, values in param_grid.items():
        dico[keys]=list(product(param_grid.values))
    param_combinations = list(product(param_grid.values()))
    kf = KFold(n_splits=k_folds, shuffle=True, random_state=42)
    best_params = None
    best_score = 0
    for keys,values in dico.items():
        for val in values.values():
            scores = []
            for train_index, test_index in kf.split(X):
                X_train, X_test = X[train_index], X[test_index]
                y_train, y_test = y[train_index], y[test_index]


        