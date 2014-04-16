__author__ = 'michal'
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.ensemble import AdaBoostRegressor


bases = {
    'A': 0,
    'C': 1,
    'G': 2,
    'T': 3,
    'N': 4,
    '-': -1,  # gap value
}

bases_reverse = {v: k for k, v in bases.iteritems()}

window_size = 5
annotations_enabled = True

classifiers = [
    (RandomForestRegressor, 'randomforest', {"n_estimators": 50, "n_jobs": 4, "max_depth": 40}),
    (ExtraTreesRegressor, 'extratrees', {"n_estimators": 50}),
    (AdaBoostRegressor, 'adaboost', {"n_estimators": 50}),
]

classifier_index = 0
