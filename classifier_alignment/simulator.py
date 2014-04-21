#!/usr/bin/python
from alignment import Fasta
from classifier_alignment.AnnotationConfig import Annotations
from tools.file_wrapper import Open
import json
import os
import random
import sys
import track
# Todo: zmena P_START_GENE
P_START_GENE = 0.01
P_STOP_GENE = 0.01
P_START_DELETE = 0.01
P_STOP_DELETE = 0.1
P_NOT_MUTATE_GENE = 0.9

P_MUTATE_DNA_11 = 0.8
P_MUTATE_DNA_1 = 0.65
P_MUTATE_DNA_00 = 0.6

DNA_CHARS = ['A', 'C', 'G', 'T']


class BiasedCoin:
    def __init__(self, p):
        self.p = p

    def flip(self):
        r = random.random()
        return r < self.p


class MarkovChain:
    def __init__(self, p, q):
        self.state = 0
        self.c = list()
        self.c.append(BiasedCoin(p))
        self.c.append(BiasedCoin(q))

    def get_state(self):
        if self.c[self.state].flip():
            self.state += 1
            self.state %= len(self.c)
        return self.state


def get_sequence(sequence, mask):
    return [s for i, s in enumerate(sequence) if mask[i] != '-']


def sequence_to_intervals(seq, name):
    last = None
    vi = list()
    for i in range(len(seq)):
        if seq[i]:
            if last is None:
                last = [i, i, name]
            last[1] += 1
        else:
            if last is not None:
                vi.append(last)
                last = None
    if last is not None:
        vi.append(tuple(last))
    return vi


def create_dna_mutation_coin(s):
    """
    set up DNA mutation coin
    """
    p = [P_MUTATE_DNA_00, P_MUTATE_DNA_1, P_MUTATE_DNA_11]
    return BiasedCoin(p[s])


def simulate(
    n,
    datadir='data/sequences/train_sequences/',
    fname='simulated_alignment',
):
    s1name = "sequence1"
    s2name = "sequence2"
    s3name = "sequence3"
    annotation_name = 'gene'

    alignment_extension = ".fa"
    annotations_extension = ".bed"
    config_extension = ".js"

    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    if len(sys.argv) > 2:
        fname = sys.argv[2]

    master_gene_sequence = MarkovChain(P_START_GENE, P_STOP_GENE)
    human_delete_sequence = MarkovChain(P_START_DELETE, P_STOP_DELETE)
    mouse_delete_sequence = MarkovChain(P_START_DELETE, P_STOP_DELETE)
    horse_delete_sequence = MarkovChain(P_START_DELETE, P_STOP_DELETE)
    mutator_coin = BiasedCoin(P_NOT_MUTATE_GENE)

    master_gene = list()
    human_gene = list()
    mouse_gene = list()
    horse_gene = list()

    human_dna = list()
    mouse_dna = list()
    horse_dna = list()

    for i in range(n):
        # create master_gene item
        g = g2 = g3 = g4 = master_gene_sequence.get_state()

        # mutate master_gene item
        if g:
            g2 = mutator_coin.flip()
            g3 = mutator_coin.flip()
            g4 = mutator_coin.flip()

        dna_mutation_coin = create_dna_mutation_coin(g2 + g3)
        dna_mutation_coin2 = create_dna_mutation_coin(g2 + g4)

        # create DNA item
        c = c2 = c3 = DNA_CHARS[random.randint(0, 3)]
        if not dna_mutation_coin.flip():
            char_index = random.randint(0, 2)
            if DNA_CHARS[char_index] == c2:
                char_index = 3
            c2 = DNA_CHARS[char_index]

        if not dna_mutation_coin2.flip():
            char_index = random.randint(0, 2)
            if DNA_CHARS[char_index] == c3:
                char_index = 3
            c3 = DNA_CHARS[char_index]

        # delete DNA item
        if human_delete_sequence.get_state():
            c = '-'
        if mouse_delete_sequence.get_state():
            c2 = '-'
        if horse_delete_sequence.get_state():
            c3 = '-'

        # add items to sequence
        master_gene.append(g)
        human_gene.append(g2)
        mouse_gene.append(g3)
        horse_gene.append(g4)

        human_dna.append(c)
        mouse_dna.append(c2)
        horse_dna.append(c3)

    # output
    s1fname = os.path.join(
        datadir, fname+'_'+s1name+'_'+annotation_name+annotations_extension
    )
    if os.path.isfile(s1fname):
        os.remove(s1fname)
    s2fname = os.path.join(
        datadir, fname+'_'+s2name+'_'+annotation_name+annotations_extension
    )
    if os.path.isfile(s2fname):
        os.remove(s2fname)
    s3fname = os.path.join(
        datadir, fname+'_'+s3name+'_'+annotation_name+annotations_extension
    )
    if os.path.isfile(s3fname):
        os.remove(s3fname)

    intervals1 = sequence_to_intervals(
        get_sequence(human_gene, human_dna), annotation_name
    )
    intervals2 = sequence_to_intervals(
        get_sequence(mouse_gene, mouse_dna), annotation_name
    )
    intervals3 = sequence_to_intervals(
        get_sequence(horse_gene, horse_dna), annotation_name
    )

    annotations = Annotations()
    annotations.setAnnotations([annotation_name])
    annotations.addSequences([s1name, s2name, s3name])
    annotations.addAnnotationFile(s1name, annotation_name,  s1fname)
    annotations.addAnnotationFile(s2name, annotation_name,  s2fname)
    annotations.addAnnotationFile(s3name, annotation_name,  s3fname)

    Fasta.save(
        [
            (s1name, ''.join(human_dna)),
            (s2name, ''.join(mouse_dna)),
            (s3name, ''.join(horse_dna))
        ],
        os.path.join(datadir, fname+alignment_extension)
    )

    with track.new(s1fname, 'bed') as t:
        t.fields = ['start', 'end', 'name']
        t.write("chr1", intervals1)
    with track.new(s2fname, 'bed') as t:
        t.fields = ['start', 'end', 'name']
        t.write("chr1", intervals2)
    with track.new(s3fname, 'bed') as t:
        t.fields = ['start', 'end', 'name']
        t.write("chr1", intervals3)

    with Open(os.path.join(datadir, fname+config_extension), "w") as f:
        json.dump(annotations.toJSON(), f)

if __name__ == "__main__":
    # simulate(10000, 'data/sequences/model_train_seq/simulated')
    # simulate(1000, 'data/sequences/simulated')
    for i in range(5):
         simulate(1000, 'data/sequences/simulated', fname='simulated_alignment{}'.format(i))
    # for i in range(20):
    #     simulate(10000, fname='simulated_alignment{}'.format(i))
    # simulate(20, 'data/test_data/sequences/', fname='alignment')

