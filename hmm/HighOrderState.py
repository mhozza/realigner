from hmm.HMM import State
from tools.Exceptions import ParseException


class HighOrderState(State):
    def __init__(self, *p):
        State.__init__(self, *p)
        self.order = 0

    def load(self, dictionary):
        State.load(self, dictionary)
        if 'order' not in dictionary:
            raise ParseException('order was not found in state')
        self.order = dictionary['order']

    def toJSON(self):
        ret = State.toJSON(self)
        ret['order'] = self.order
        return ret

    def getEmissionText(self, X, x, dx):
        wat = X[x : x + dx]
        if x - self.order >= 0:
            base = x - self.order
            wat = X[base : base + dx] + wat
#        print self.stateName, self.order, len(X), x, dx, wat
        return wat

    def emission(self, X, x, dx):
        # If you change this, change also getEmissionText
        wat = X[x : x + dx]
        if x - self.order >= 0:
            base = x - self.order
            wat = X[base : base + dx] + wat
        return self.emissions[wat]



