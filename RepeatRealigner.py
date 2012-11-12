import AlignmentIterator
from LogNum import LogNum
import sys

class RepeatRealigner:
    
    def __init__(self, alignment = None, X = None, Y = None, width = -1):
        self.width = width
        self.sequenceX = X
        self.sequenceY = Y
        self.alignment = alignment
        self.Forward = None
        self.Backward = None
        self.Posterior = None
        if alignment != None:
            if X != None or Y != None:
                raise "If you provide alignment, do not provide sequences."
            self.setBaseAlignment(alignment)
        else:
            self.setSequences(X, Y)
            # We do not have reference alignment. 
    
    def setBaseAlignment(self, alignment):
        self.alignment = alignment
        if len(alignment) < 2:
            raise "We need alignment of at least two sequences"
        if len(alignment) > 2:
            sys.stderr.write("Warning: Provided alignment of more than two " +
                             "sequences. Using only first two, ignoring " +
                             "others.\n")
        self.sequenceX = alignment[0].translate(None, '-')
        self.sequenceY = alignment[1].translate(None, '-')
    
    def setWidth(self, width):
        self.width = width
        
    def setSequences(self, X, Y):
        if X == None or Y == None:
            raise "Two sequences needed."
        self.alignment = None
        self.sequenceX = X
        self.sequenceY = Y
        self.alignment = None
    
    def loadModel(self, filename):
        #TODO: get all 
        return
    
    def getGenerator(self):
        if self.width == None: 
            self.width = -1
        if self.alignment == None:
            tupleList = AlignmentIterator.TextAlignmentToTupleList(
                self.sequenceX, 
                self.sequenceY)
            return AlignmentIterator.FullAlignmentGenerator(
                tupleList,
                self.width)
        else:
            return AlignmentIterator.AlignmentBeamGenerator(
                self.alignment,
                self.width)
            
    def createTable(self, length):
        x = dict()
        x.setdefault(LogNum(0))
        y = dict()
        y.setdefault(x)
        table = list()
        for _ in range(length):
            table.append(dict(y))
        return table
            
    
    def ComputePosterior(self):
        positions = self.getGenerator()
        for p in positions: 
            for key, value in self.Forward[p[0]][p[1]].iteritems():
                self.Posterior[p[0]][p[1]][key] = value * \
                    self.Backward[p[0]][p[1]][key] # todo -- toto by som upravil
            
    def ComputeAlignment(self):
        return
    
    def realign(self):
        self.Forward = self.createTable(len(self.sequenceX) + 1)
        self.Backward = self.createTable(len(self.sequenceX) + 1)
        self.Posterior = self.createTable(len(self.sequenceX) + 1)
        #self.ComputeForward()
        #self.ComputeBackward()
        self.ComputePosterior()
    


if __name__ == "__main__":
    print("HoHoHo")