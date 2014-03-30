"""
@author: Michal Hozza
"""


class FakeMatchClassifier():
    def __init__(self):
        pass

    def predict(self, data):
        pass

    def load(self, f):
        pass

    def save(self, f):
        pass

    def fit(self, data):
        pass


class FakeIndelClassifier(FakeMatchClassifier):
    def __init__(self):
        FakeMatchClassifier.__init__(self)

    def predict(self, data):
        pass
