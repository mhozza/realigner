import bisect


class RepeatGenerator:
    
    def __init__(self, repeats=None, width=0):
        self.repeats = []
        self.vals = []
        self.rrepeats = []
        self.rvals = []
        self.width = width
        if repeats != None:
            self.addRepeats(repeats)
            self.buildRepeatDatabase()
        
    def addRepeats(self, repeats):
        self.repeats.extend(repeats)
        
    def deleteRepeats(self):
        self.repeats = []
        
    def buildRepeatDatabase(self):
        self.repeats = sorted(self.repeats, key=lambda x: x.start)
        self.vals = [r.start for r in self.repeats]
        self.rrepeats = sorted(self.repeats, key=lambda x: x.end)
        self.rvals = [r.end for r in self.rrepeats]
        
    def getHints(self, position):
        low = bisect.bisect_left(self.vals, position - self.width)
        high = bisect.bisect_right(self.vals, position + self.width)
        for pos in range(low, high):
            rep = self.repeats[pos]
            length = len(rep.sequence)
            length += rep.start - position
            dd = self.width
            if dd == 0:
                dd = 1
            for d in range(dd):
                yield(length + d, rep.consensus)

        
    def getReverseHints(self, position):
        low = bisect.bisect_left(self.rvals, position - self.width)
        high = bisect.bisect_right(self.rvals, position + self.width)
        for pos in range(low, high):
            rep = self.rrepeats[pos]
            length = len(rep.sequence)
            length += position - rep.end
            dd = self.width
            if dd == 0:
                dd = 1
            for d in range(dd):
                yield (length + d, rep.consensus)