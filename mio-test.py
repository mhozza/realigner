#!/usr/bin/python
__author__ = 'michal'

import os
from os import path, listdir
import threading
import argparse
from classifier_alignment import transitivitycheck


def realign(src, dest, sX, sY, model):
    model_dir = 'data/models'
    os.system(
        './mio-test.sh {} {} {} {} {}'.format(
            src, dest, sX, sY, os.path.join(model_dir, model)
        )
    )


def main(base_filename='simulated_alignment', base_dir='data/sequences'):
    # models = ['SimpleHMM2.js', 'ClassificationHMM.js', 'OracleHMM.js']
    # models = ['SimpleHMM2.js']
    models = ['ClassificationHMM.js', 'OracleHMM.js']
    # models = ['SimpleHMM2Bio.js', 'ClassificationHMMBio.js', 'OracleHMMBio.js']
    # models = ['SimpleHMM2Test.js', 'ClassificationHMMTest.js', 'OracleHMMTest.js']
    # models = ['ClassificationHMMBio.js']#, 'OracleHMMBio.js']
    src = os.path.join(base_dir, base_filename)
    sequences = ['sequence1', 'sequence2', 'sequence3']
    # sequences = ['sequence1', 'sequence2']

    for model in models:
        dst = os.path.join(base_dir, 'realigned/' + path.splitext(base_filename )[0] + '.{}_{}.' + model + '.fa')
        threads = list()

        for x in range(len(sequences)-1):
            for y in range(x+1, len(sequences)):
                sX = sequences[x]
                sY = sequences[y]
                if sX != sY:
                    dest = dst.format(sX, sY)
                    threads.append(
                        threading.Thread(target=realign, args=(src, dest, sX, sY, model))
                    )

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        print model
        if len(sequences) == 3:
            print 'Transitivity: ' + str(transitivitycheck.score(dst))
        sX = sequences[0]
        sY = sequences[1]
        print 'Equality: ' + str(transitivitycheck.compare_with_source(src, dst.format(sX, sY), sX, sY))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name', metavar='name', type=str, default='simulated_alignment', nargs='?')
    parser.add_argument('dir', metavar='dir', type=str, default='data/sequences/simulated', nargs='?')
    parser.add_argument('--multi', action="store_true")
    args = parser.parse_args()
    if args.multi:
        sequences = list()
        for fn in filter(
            lambda x: path.splitext(x)[1] == '.fa' and args.name in path.splitext(x)[0], listdir(args.dir)
        ):
            if path.isfile(path.join(args.dir, fn)):
                main(fn, args.dir)
    else:
        main(args.name+'.fa', args.dir)
