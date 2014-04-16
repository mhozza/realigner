from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, AdaBoostRegressor
from classifier_alignment.DataPreparer import DataPreparer, IndelDataPreparer
from classifier_alignment.ComparingDataPreparer import ComparingDataPreparer,\
    ComparingIndelDataPreparer
from classifier_alignment.FullComparingDataPreparer import FullComparingDataPreparer,\
    FullComparingIndelDataPreparer


classifiers = [
    (RandomForestRegressor, 'randomforest', {"n_estimators": 50, "n_jobs": 4, "max_depth": 40}),
    (ExtraTreesRegressor, 'extratrees', {"n_estimators": 50}),
    (AdaBoostRegressor, 'adaboost', {"n_estimators": 50}),
]

classifier_index = 2

preparers = [
    (DataPreparer, IndelDataPreparer, ''),
    (ComparingDataPreparer, ComparingIndelDataPreparer, '_cmp_'),
    (FullComparingDataPreparer, FullComparingIndelDataPreparer, '_fullcmp_'),
]

preparer_index = 1
