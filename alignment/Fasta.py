#Alignment sa load
from Alignment import Alignment
from tools.file_wrapper import Open

def loadGenerator(filename): 
    with Open(filename, 'r') as f:
        seq_name = ""
        sequence = ""
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] == '>':
                if len(sequence) > 0:
                    yield (seq_name, sequence)
                seq_name = line[1:]
                sequence = ""
            else:
                sequence += line.strip()
        if len(sequence) > 0:
            yield (seq_name, sequence)
    
def load(filename):
    return Alignment(loadGenerator(filename))
   
def save(alignment, filename, width = 80):
    f = Open(filename, "w")
    for (seq_name, sequence) in alignment:
        seq_length = len(sequence)
        f.write(">" + seq_name + "\n")
        if width <= 0: 
            width = seq_length
        count = seq_length / width
        for i in range(count):
            f.write(sequence[i * width: (i+1) * width] + "\n")
        if count * width < seq_length:
            f.write(sequence[count * width:] + "\n") 
    f.close()
    
def alnToSeq(sequence):
    return sequence.replace("-","")