from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, AdaBoostClassifier
from classifier_alignment.DataPreparer import DataPreparer, IndelDataPreparer
from classifier_alignment.ComparingDataPreparer import ComparingDataPreparer,\
    ComparingIndelDataPreparer
from classifier_alignment.FullComparingDataPreparer import FullComparingDataPreparer,\
    FullComparingIndelDataPreparer
from classifier_alignment.CombinedDataPreparer import CombinedDataPreparer,\
    CombinedIndelDataPreparer
from classifier_alignment.UnionDataPreparer import UnionDataPreparer,\
    UnionIndelDataPreparer


classifiers = [
    (RandomForestClassifier, 'randomforest', {"n_estimators": 50, "n_jobs": 4, "max_depth": 40}),
    (ExtraTreesClassifier, 'extratrees', {"n_estimators": 50}),
    (AdaBoostClassifier, 'adaboost', {"n_estimators": 50}),
]

classifier_index = 0

preparers = [
    (DataPreparer, IndelDataPreparer, ''),
    (ComparingDataPreparer, ComparingIndelDataPreparer, '_cmp_'),
    (FullComparingDataPreparer, FullComparingIndelDataPreparer, '_fullcmp_'),
    (CombinedDataPreparer, CombinedIndelDataPreparer, '_combined_'),
    (UnionDataPreparer, UnionIndelDataPreparer, '_union_'),
]
preparer_index = 3

same_classifier = False
