#!/usr/bin/python
import os
import sys
import json
import track
import argparse
import pandas as pd
from alignment import Fasta
from classifier_alignment import simulator
from classifier_alignment.maf_loader import MafLoader
from functools import partial
from collections import defaultdict

seq_basename = 'sequence'
overwrite = True


def load_seq():
    seq1 = sys.stdin.readline()
    seq2 = sys.stdin.readline()
    return [seq1, seq2]


def checkfile(fname):
    if os.path.isfile(fname):
        if overwrite:
            print 'removing existing file', fname
            os.remove(fname)
        else:
            print 'skipping existing file', fname
            return True


def create_fasta(fname, seq_basename, sequences, rename=False):
    if rename:
        names = [seq_basename + str(i+1) for i in range(len(sequences))]
    else:
        names = [s['name'] for s in sequences]
    assert(len(names) == len(sequences))
    seq = [s['sequence'].upper() for s in sequences]
    Fasta.save(zip(names, seq), fname)
    return names


def create_repeat_annotation(sequence, fname):
    if checkfile(fname):
        return
    annotation = (x.isupper() for x in sequence)
    intervals = simulator.sequence_to_intervals(
        simulator.get_sequence(annotation, sequence), 'repeat'
    )
    with track.new(fname, 'bed') as t:
        t.fields = ['start', 'end', 'name']
        t.write("chr1", intervals)


def create_gene_annotation(source_fname, chromosome, fname):
    if checkfile(fname):
        return
    genes = pd.read_csv(source_fname, sep='\t', header=None)
    if 'hg19' in source_fname:
        indices = [2, 4, 5]
    else:
        indices = [1, 3, 4]
    genes = genes[genes[indices[0]] == chromosome]
    genes['desc'] = 'gene'
    genes = genes[indices + ['desc']]
    genes.to_csv(fname, sep='\t', header=['track type="bed"', 'converted_by="mio"', '', ''])


def create_config(fname, annotations, names, annotation_files):
    sequences = [
        {'name': name, 'annotations': annotation_files[name]} for name in names
    ]

    data = {
        '__name__': 'Annotations',
        'annotations': annotations,
        'sequences': sequences,
    }
    f = open(fname, 'w')
    json.dump(data, f)
    f.close()


def make_annotation_fname(
    data_dir,
    base_fname,
    sequence_name,
    annotation_name,
    template='{basename}_{sequence}.{annotation}.bed'
):
    return os.path.join(
        data_dir,
        template.format(basename=base_fname, annotation=annotation_name, sequence=sequence_name),
    )


def extract_seq_info(seq_name):
    org, chrom = seq_name.split('.')
    return org, chrom


def make_alignment(sequences, rename=False, base_fname='bio', data_dir='data/sequences/bio'):
    def add_annotation(seq_name, name, fname_func, ann_func, offset=0):
        filename = fname_func(name)
        annotation_files[seq_name].append({'id': name, 'file': filename, 'offset': offset})
        ann_func(filename)

    seq_fname = os.path.join(data_dir, base_fname + '.fa')
    config_fname = os.path.join(data_dir, base_fname + '.js')
    annotations = ['gene', 'repeat']
    annotation_files = defaultdict(list)
    names = create_fasta(seq_fname, seq_basename, sequences, rename)
    for seq_name, s in zip(names, sequences):
        make_fname = partial(make_annotation_fname, data_dir, base_fname, s['name'])
        org, chrom = extract_seq_info(s['name'])
        repeat = partial(create_repeat_annotation, s['sequence'])
        add_annotation(seq_name, 'repeat', make_fname, repeat)
        gene = partial(create_gene_annotation, 'data/sequences/bio/genscan.{}.txt'.format(org), chrom)
        add_annotation(seq_name, 'gene', make_fname, gene, offset=s['offset'])
    create_config(config_fname, annotations, names, annotation_files)


def make_from_maf(
    fname,
    sequences,
    min_size=0,
    limit=None,
    base_fname='bio',
    data_dir='data/sequences/bio'
):
    loader = MafLoader(fname)
    for i, (alignment, _) in enumerate(loader.filtered_alignments(sequences, min_size, remove_other=True)):
        if limit is not None:
            if limit == 0:
                break
            limit -= 1
        print 'make_alignment', i
        make_alignment(alignment, base_fname='bio'+str(i), rename=True)


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('name', metavar='name', type=str)
    # args = parser.parse_args()
    # sequences = load_seq()
    # main(sequences, args.name)
    make_from_maf('data/sequences/bio/chr1.maf', ['hg19', 'panTro2.chr1$', 'canFam2'], 1000)
