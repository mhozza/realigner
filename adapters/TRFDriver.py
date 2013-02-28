"""
Wrapper for tandem repeat finder
"""
import subprocess
import os


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
            mathType=float
        ):
        self.path = 'trf'
        self.mathType=mathType
        if self.path != None:
            self.setPath(path)
    
       
    def setPath(
        self,
        path,
    ):
        """
        Set path
        """
        if type(path) == list:
            for p in path:
                if os.path.exists(p):
                    self.path = p 
        
    def run(
            self, 
            sequencefile,
            paramSeq=None,
            dont_parse=False
        ):
        """
        Run tandem repeat finder and return repeats
        """
        if paramSeq == None:
            paramSeq = ["2", "7", "7", "80", "10", "0", "500", "-h"]
        pseq = [self.path, os.path.basename(sequencefile)]
        pseq.extend(paramSeq)
        #print self.path
        current_path = os.getcwd()
        #print current_path
        #print os.path.dirname(sequencefile)
        os.chdir(os.path.dirname(sequencefile))
        #print os.getcwd()
        process = subprocess.Popen(pseq, stdout=subprocess.PIPE, 
                                   stderr=subprocess.STDOUT)
        _, _ = process.communicate()
        process.poll()
        os.chdir(current_path)
        #print(output)
        pseq.pop()
        pseq.append("dat")   
        output_file = ".".join(pseq[1:])
        if dont_parse:
            return os.path.dirname(sequencefile) + '/' + output_file
        f = open(output_file, "r")
        output = {}
        sequence_name = ""
        repeats = []
        for line in f:
            line = [x.strip() for x in line.strip().split(' ')]
            if len(line) < 2:
                continue
            if line[0] == 'Sequence:':
                if sequence_name != "":
                    output[sequence_name] = repeats
                    repeats = []
                sequence_name = " ".join(line[1:])
                continue
                    
            if len(line) < 15:
                continue
            repeats.append(
                Repeat(int(line[0]) -1 , int(line[1]), self.mathType(line[3]),
                       line[13], line[14]))
        if len(repeats) > 0 and sequence_name != "":
            output[sequence_name] = repeats
        return output