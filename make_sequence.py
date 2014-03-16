#!/usr/bin/python
import os
import sys
import json
import track
import argparse
from alignment import Fasta
from classifier_alignment import simulator


def load_seq():
    seq1 = sys.stdin.readline()
    seq2 = sys.stdin.readline()
    return [seq1, seq2]


def create_fasta(fname, seq_basename, sequences):
    names = []
    for i, _ in enumerate(sequences):
        names.append(seq_basename + str(i+1))
    seq2 = [s.upper() for s in sequences]
    Fasta.save(zip(names, seq2), fname)
    return names


def cerate_repeat_annotation(fname, sequence, name):
    annotation = (x.isupper() for x in sequence)
    intervals = simulator.sequence_to_intervals(
        simulator.get_sequence(annotation, sequence), name
    )
    with track.new(fname, 'bed') as t:
        t.fields = ['start', 'end', 'name']
        t.write("chr1", intervals)


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


def add_annotation(
        sequences,
        annotations,
        annotation_files,
        name,
        filename_template,
        func,
        args,
):
    annotations.append(name)
    for seq_name, seq in sequences:
        filename = filename_template.format(seq_name)
        if not seq_name in annotation_files:
            annotation_files[seq_name] = list()
        annotation_files[seq_name].append({'id': name, 'file': filename})
        func(filename, seq, seq_name, *args)


def main(base_fname='bio'):
    data_dir = 'data/bio_seq'
    seq_fname = os.path.join(data_dir, base_fname + '.fa')
    config_fname = os.path.join(data_dir, base_fname + '.js')
    seq_basename = 'sequence'
    annotations = list()
    annotation_files = dict()
    sequences = load_seq()
    names = create_fasta(seq_fname, seq_basename, sequences)
    add_annotation(
        zip(names, sequences),
        annotations,
        annotation_files,
        'repeat',
        os.path.join(data_dir, base_fname + '_{}.repeat.bed'),
        cerate_repeat_annotation,
        [],
    )
    create_config(config_fname, annotations, names, annotation_files)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name', metavar='name', type=str)
    args = parser.parse_args()
    main(args.name)
