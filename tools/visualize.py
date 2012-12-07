import matplotlib.pyplot as pyplot
from tools import structtools
from collections import defaultdict

def getPairIterator(X):
    tp = type(X)
    if tp == type(defaultdict()): tp = type(dict())
    if tp == type(list()):
        return X
    elif tp == type(dict()):
        return X.iteritems()
    else:
        return X

def containNonzeroElement(val):
    tp = type(val)
    if tp == type(list()) or tp == type(dict()) or tp == type(tuple):
        for (_, v) in getPairIterator(val):
            if containNonzeroElement(v):
                return True
    if val > 0.0:
        return True
    return False

class Vis2D:
    
    def __init__(self):
        self.fig = pyplot.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True)
        
    def addFigure(self, X, Y, type, color=None):
        if color == None:
            self.ax.plot(X, Y, type)
        else:
            self.ax.plot(X, Y, type, color=color)
            
    def addTable(self, table, tp, color=None, function=None,
                 xdx=0.0, ydx=0.0):
        X = []
        Y = []
        if function == None:
            function = lambda _: True
        for (x, xval) in getPairIterator(table):
            for (y, yval) in getPairIterator(xval):
                if function(yval):
                    X.append(x + xdx)
                    Y.append(y + ydx)
            
        self.addFigure(X, Y, tp, color=color)
    
    def addPositionGenerator(self, generator, tp, color=None, xdx=0.0, ydx=0.0):
        X = [x + xdx for (x, _) in generator]
        Y = [x + ydx for (_, x) in generator]        
        self.addFigure(X, Y, tp, color)
        
    def show(self):
        pyplot.show()