from hmm.HMM import State
from models import SpecialHMMs


class RepeatProfileFactory:
            
    def __init__(self, mathType=float):
        self.a = 2
        self.cache = dict()
        self.mathType = mathType
        
    def getHMM(self, consensus):
        if consensus in self.cache:
            return self.cache[consensus]
        self.cache[consensus] = SpecialHMMs.createProfileHMM(self.mathType, 
            consensus, 23.0, 
            [("A", 0.25), ("C", 0.25), ("G", 0.25), ("T", 0.25)], {
                "MM": 0.92, "MI": 0.04, "MD": 0.04,
                "IM": 0.1, "II": 0.85, "ID": 0.05,
                "DM": 0.1, "DI": 0.1, "DD": 0.8,
                "_M": 0.8, "_I": 0.1, "_D": 0.1,
            }) #TODO
        return self.cache[consensus]
        
    
    

class PairRepeatState(State):
    
    def __init__(self, *p):
        State.__init__(self, *p)
        self.hmm = None
        self.factory = RepeatProfileFactory()
        self.repeatGeneratorX = None
        self.repeatGeneratorY = None
        self.consensus = ""
        self.memoizeX = dict()
        self.memoizeY = dict()
        self.dgmemoize = dict()
        self.rdgmemoize = dict()
        
    
    def addRepeatGenerator(self, repeatGeneratorX, repeatGeneratorY):
        self.repeatGeneratorX = repeatGeneratorX
        self.repeatGeneratorY = repeatGeneratorY

        
    def load(self, dictionary):
        State.load(self, dictionary)
        
    
    def durationGenerator(self, _x, _y):
        key = (_x, _y)
        if key in self.dgmemoize:
            return self.dgmemoize[key]
        val = list(self._durationGenerator(_x, _y))
        self.dgmemoize[key] = val
        return val
    
    def _durationGenerator(self, _x, _y):
        X = list(self.repeatGeneratorX.getHints(_x))
        Y = list(self.repeatGeneratorY.getHints(_y))
        N = len(X) * len(Y)
        p = self.mathType(0.0)
        if N > 0:
            p = self.mathType(1.0 / float(N))
        for (xlen, xcon) in X:
            for (ylen, ycon) in Y:
                self.consensus = xcon
                yield((xlen, ylen), p)
                self.consensus = ycon
                yield((xlen, ylen), p)
    
    
    def reverseDurationGenerator(self, _x, _y):
        key = (_x, _y)
        if key in self.rdgmemoize:
            return self.rdgmemoize[key]
        val = list(self._reverseDurationGenerator(_x, _y))
        self.rdgmemoize[key] = val
        return val
    
    def _reverseDurationGenerator(self, _x, _y):
        X = list(self.repeatGeneratorX.getReverseHints(_x))
        Y = list(self.repeatGeneratorY.getReverseHints(_y))
        N = len(X) * len(Y)
        p = self.mathType(0.0)
        if N > 0:
            p = self.mathType(1.0 / float(N))
        for (xlen, xcon) in X:
            for (ylen, ycon) in Y:
                self.consensus = xcon
                yield((xlen, ylen), p)
                self.consensus = ycon
                yield((xlen, ylen), p)
        
        
    def emission(self, X, x, dx, Y, y, dy):
        # we expect that we have consensus from last generated duration
        #key = (self.consensus, x, dx)
        #if key in self.memoizeX:
        #    return self.memoizeX[key]
        #hmm = self.factory.getHMM(self.consensus)
        #val = hmm.getProbability(X, x, dx) * hmm.getProbability(Y, y, dy)
        #self.memoizeX[key] = val
        #return val      
        keyX = (self.consensus, x, dx)
        keyY = (self.consensus, y, dy)
        hmm = None
        if keyX in self.memoizeX:
            valX = self.memoizeX[keyX]
        else:
            hmm = self.factory.getHMM(self.consensus)
            valX = hmm.getProbability(X, x, dx)
            self.memoizeX[keyX] = valX
        if keyY in self.memoizeY:
            valY = self.memoizeY[keyY]
        else:
            if hmm == None:
                hmm = self.factory.getHMM(self.consensus)
            valY = hmm.getProbability(Y, y, dy)
            self.memoizeY[keyY] = valY
        return valX * valY