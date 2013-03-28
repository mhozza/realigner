'''
Created on Mar 28, 2013

@author: Michal Hozza
'''
from copy import deepcopy
import pickle
from sklearn.ensemble import RandomForestClassifier
#from numpy import mean


class AnnotatedBase:
    def __init__(self):
        self.base = -1
        self.annotations = {}

    def copy(self, ab):
        self.base = ab.base
        self.annotations = deepcopy(ab.annotations)


class AnnotatedBaseCouple:
    def __init__(self, annotations = []):
        self.annotations = annotations
        self.X = AnnotatedBase()
        self.Y = AnnotatedBase()

    def toArray(self):
        a = [self.X.base, self.Y.base]

        for annotation in self.annotations:
            try:
                a.append(self.X.annotations[annotation])
            except KeyError, e:
                a.append(-1)

            try:
                a.append(self.Y.annotations[annotation])
            except KeyError, e:
                a.append(-1)
        return a



class PairClassifier:
	def __init__(self):
		self.classifier = RandomForestClassifier(n_estimators=10, n_jobs=4)		

    def load(self, file):
    	self.classifier = pickle.load(file)
    
    def save(self, file):
    	pickle.dump(self.classifier, file)

    def fit(self, data, target):
    	self.classifier.fit(data, target)

    def predict(self, data):
#    	return self.classifier.predict(data)
#        hits = array([tree.predict(data) for tree in self.classifier.estimators_])
#        return [mean(hits[:,i]) for i in range(len(data))]
        return self.classifier.predict_proba(data)




    