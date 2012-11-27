"""
Wrapper for tandem repeat finder
"""
import subprocess

class Repeat:
    """
    Repeat data structure
    """
    def __init__(
            self,
            start=0, 
            end=0, 
            repetitions=0, 
            consensus="",
            sequence="",
        ):
        self.start = start
        self.end = end
        self.repetitions = repetitions
        self.consensus = consensus
        self.sequence = sequence

class TRFDriver:
    """
    Wrapper for tandem repeat finder
    """
    def __init__(
            self,
            path=None,
        ):
        self.path = 'trf'
        if self.path != None:
            self.setPath(path)
    
       
    def setPath(
        self,
        path,
    ):
        """
        Set path
        """
        self.path = path
    
        
    def run(
            self, 
            sequencefile,
            paramSeq=None,
        ):
        """
        Run tandem repeat finder and return repeats
        """
        if paramSeq == None:
            paramSeq = ["2", "7", "7", "80", "10", "0", "500"]
        pseq = [self.path]
        pseq.extend(paramSeq)
        pseq.append(sequencefile)
        subprocess.call(pseq)
        pseq.pop()
        pseq[0] = sequencefile
        pseq.append("dat")
        outputfile = ".".join(pseq)
        f = open(outputfile, "r")
        output = []
        for line in f:
            line = [x.split() for x in line.strip().split(' ')]
            if len(line) < 15:
                continue
            output.append(
                Repeat(int(line[0]), int(line[1]), float(line[3]), line[13], 
                       line[14]))
        return output