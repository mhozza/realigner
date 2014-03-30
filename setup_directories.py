#!/usr/bin/python
import argparse
import os


def replace_symlink(symlink, source):
    print symlink, '->', source
    os.remove(symlink)
    os.symlink(source, symlink)


def set_sequence(seq):
    path = 'data'
    dirs = {
        'bio': {
            'clf': 'clf_bio',
            'sequences': 'bio',
            'train': 'train_bio',
            'model_train': 'bio',
        },
        'simulated': {
            'clf': 'clf_simul',
            'sequences': 'simulated',
            'train': 'train_simulated',
            'model_train': 'simul',
        },
        'test': {
            'clf': 'clf_test',
            'sequences': 'test',
            'train': 'train_test',
            'model_train': 'test',
        },
    }

    symlinks = {'clf': 'clf', 'train': 'sequences/train_sequences'}

    for link in symlinks:
        replace_symlink(
            os.path.join(path, symlinks[link]),
            dirs[seq][link],
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('seq', type=str)
    args = parser.parse_args()
    set_sequence(args.seq)
