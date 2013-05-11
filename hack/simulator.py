#!/usr/bin/python
from alignment import Fasta
from hack.AnnotationConfig import Annotations
from tools.file_wrapper import Open
import json
import os
import random
import sys
import track


class BiasedCoin:
    def __init__(self, p):
        self.p = p

    def flip(self):
        r = random.random()
        return (r < self.p)


class MarkovChain:
    def __init__(self, p, q):
        self.state = 0
        self.c = list()
        self.c.append(BiasedCoin(p))
        self.c.append(BiasedCoin(q))

    def getState(self):
        if(self.c[self.state].flip()):
            self.state+=1
            self.state%=len(self.c)
        return self.state

def getSequence(sequence, mask):
    return [sequence[i] for i in range(len(sequence)) if mask[i]!='-']

def sequenceToIntervals(seq, name):
    last = None;
    vi = list()
    for i in range(len(seq)):
        if seq[i]:
            if last==None:
                last = [i, i, name]
            last[1]+=1
        else:
            if last!=None:
                vi.append(last)
                last = None
    if last != None:
        vi.append(tuple(last))
    return vi

P_START_GENE = 0.001
P_STOP_GENE = 0.01
P_START_DELETE = 0.01
P_STOP_DELETE = 0.1
P_NOT_MUTATE_GENE = 0.9
P_MUTATE_DNA_11 = 0.8
P_MUTATE_DNA_1 = 0.7
P_MUTATE_DNA_00 = 0.65

DNA_CHARS = ['A', 'C', 'G', 'T']

def createDNAMutationCoin(s):
    '''
    set up DNA mutation coin
    '''
    p = [P_MUTATE_DNA_00, P_MUTATE_DNA_1, P_MUTATE_DNA_11]
    return BiasedCoin(p[s])


sXname = "sequence1"
sYname = "sequence2"
annotationName = 'gene'

datadir = 'data/train_sequences/'
fname = "simulated_alignment"
alignmentExtension = ".fa"
annotationsExtension = ".bed";
configExtension = ".js"

n = 1000;

if len(sys.argv)>1:
    n = int(sys.argv[1])
if len(sys.argv)>2:
    fname = sys.argv[2]

# srand(time(NULL));

masterGeneSequence = MarkovChain(P_START_GENE,P_STOP_GENE)
humanDeleteSequence = MarkovChain(P_START_DELETE,P_STOP_DELETE)
mouseDeleteSequence = MarkovChain(P_START_DELETE,P_STOP_DELETE)
mutatorCoin = BiasedCoin(P_NOT_MUTATE_GENE)

masterGene = list()
humanGene = list()
mouseGene = list()

humanDNA = list()
mouseDNA = list()

for i in range(n):
    # create masterGene item
    g = g2 = g3 = masterGeneSequence.getState()

    # mutate masterGene item
    if(g):
        g2 = mutatorCoin.flip()
        g3 = mutatorCoin.flip()

    DNAMutationCoin = createDNAMutationCoin(g2+g3)

    # create DNA item
    c = c2 = DNA_CHARS[random.randint(0,3)]
    if not DNAMutationCoin.flip():
        char_index = random.randint(0,2)
        if(DNA_CHARS[char_index]==c2):
            char_index = 3
        c2 = DNA_CHARS[char_index]

    # delete DNA item
    if(humanDeleteSequence.getState()):
        c = '-';
    if(mouseDeleteSequence.getState()):
        c2 = '-';

    # add items to sequence
    masterGene.append(g)
    humanGene.append(g2)
    mouseGene.append(g3)

    humanDNA.append(c)
    mouseDNA.append(c2)

# output
sXfname = datadir+fname+'_'+sXname+'_'+annotationName+annotationsExtension
sYfname = datadir+fname+'_'+sYname+'_'+annotationName+annotationsExtension
intervalsX = sequenceToIntervals(getSequence(humanGene, humanDNA), annotationName)
intervalsY = sequenceToIntervals(getSequence(mouseGene, mouseDNA), annotationName)

annotations = Annotations()
annotations.setAnnotations([annotationName])
annotations.addSequences([sXname, sYname])
annotations.addAnnotationFile(sXname, annotationName,  sXfname)
annotations.addAnnotationFile(sYname, annotationName,  sYfname)

if os.path.isfile(sXfname):
    os.remove(sXfname)
if os.path.isfile(sYfname):
    os.remove(sYfname)

Fasta.save([(sXname, ''.join(humanDNA)), (sYname, ''.join(mouseDNA) )], datadir+fname+alignmentExtension)
with track.new(sXfname, 'bed') as t:
    t.fields = ['start', 'end', 'name']
    t.write("chr1", intervalsX)
with track.new(sYfname, 'bed') as t:
    t.fields = ['start', 'end', 'name']
    t.write("chr1", intervalsY)
with Open(datadir+fname+configExtension,"w") as f:
    json.dump(annotations.toJSON(),f)
