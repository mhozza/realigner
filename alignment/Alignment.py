class Alignment:
    
    def __init__(self, sequences):
        self.sequences = list()
        self.names = list()
        self.memoryhints = list()
        self.seq_to_aln = list()
        self.aln_to_seq = list()
        self.addSequences(sequences)
        
        
    
    def addSequences(self, sequences):
        for sequence in sequences:
            name = ""
            if type(sequence) == tuple:
                name = sequence[0]
                sequence = sequence[1]
            self.sequences.append(sequence)
            self.names.append(name)
            self.seq_to_aln.append(list())
            self.aln_to_seq.append(list())            
            self.computeMemoryHint(len(self.sequences) - 1)
        
        
    def computeMemoryHint(self, index):
        self.seq_to_aln[index] = list()
        self.aln_to_seq[index] = list()
        x = -1;
        for i in range(len(self.sequences[index])):
            if self.sequences[index][i] != '-':
                self.seq_to_aln[index].append(i)
                x += 1
            self.aln_to_seq[index].append(x)
        #Add end of the sequence TODO: maybe we want to remove this
        self.seq_to_aln[index].append(len(self.sequences[index]))