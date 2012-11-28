from HMM import State
import SpecialHMMs


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
            [("A", 0.25), ("C", 0.25), ("G", 0.25), ("T", 0.25)], {})
        return self.cache[consensus]
        
    
    

class PairRepeatState(State):
    
    def __init__(self, *p):
        State.__init__(self, *p)
        self.hmm = None
        self.factory = RepeatProfileFactory()
        self.repeatGeneratorX = None
        self.repeatGeneratorY = None
        self.consensus = ""
        
    
    def addRepeatGenerator(self, repeatGeneratorX, repeatGeneratorY):
        self.repeatGeneratorX = repeatGeneratorX
        self.repeatGeneratorY = repeatGeneratorY

        
    def load(self, dictionary):
        State.load(self, dictionary)
        
    
    def durationGenerator(self, _x, _y):
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
        hmm = self.factory.getHMM(self.consensus)
        return \
            hmm.getProbability(X, x, dx) * \
            hmm.getProbobility(Y, y, dy)