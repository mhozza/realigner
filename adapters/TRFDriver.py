"""
Wrapper for tandem repeat finder
"""
import subprocess
import os

trf_paths = [
   "/cygdrive/c/cygwin/bin/trf407b.dos.exe",
   "C:\\cygwin\\bin\\trf407b.dos.exe",
   "/home/mic/Vyskum/duplikacie/trf404.linux64",
   "/home/mic/bin/trf404.linux64",
   "/home/mic/bin/trf407b.linux64",
]

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
            score=0,
        ):
        self.start = start
        self.end = end
        self.repetitions = repetitions
        self.consensus = consensus
        self.sequence = sequence
        self.score = score


class TRFDriver:
    """
    Wrapper for tandem repeat finder
    """
    def __init__(
            self,
            path=None,
            mathType=float
        ):
        self.path = None
        if self.path == None:
            self.path = trf_paths
        self.mathType=mathType
        if path != None:
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
        else:
            self.path = path
        
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
            paramSeq = ["2", "3", "3", "80", "10", "0", "2000", "-h"]
        pseq = [self.path, os.path.basename(sequencefile)]
        pseq.extend(paramSeq)
        pseq2 = list(pseq)
        pseq2.pop()
        pseq2.append("dat")   
        output_file = ".".join(pseq2[1:])
        returned_file = os.path.dirname(sequencefile) + '/' + output_file
        if not os.path.exists(returned_file) or \
            os.path.getmtime(sequencefile) >= os.path.getmtime(returned_file):
            current_path = os.getcwd()
            os.chdir(os.path.dirname(sequencefile))
            process = subprocess.Popen(pseq, stdout=subprocess.PIPE, 
                                       stderr=subprocess.STDOUT)
            _, _ = process.communicate()
            process.poll()
            os.chdir(current_path)
        if dont_parse:
            return returned_file
        f = open(returned_file, "r")
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
                       line[13], line[14], line[7]))
        if sequence_name != "":
            output[sequence_name] = repeats
        return output
