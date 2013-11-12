import argparse
from tools import perf
from tools.file_wrapper import Open
import json
import re
from alignment import Fasta


def main(files_filename, output_filename):
    X = ""
    Y = ""
    A = ""
    files = json.load(Open(files_filename))
    total = len(files)
    done = 0
    for filename in files:
        if done %100 ==0:
            print '{}/{}'.format(done, total)
        done += 1
        old_filename = filename
        keep = False
        
        if filename.count('keep') == 0:
            filename = filename[:-2] + "blockRepeatRealignerTrfLot.fa"
            try:
                with Open(filename, 'r') as f:
                    l = len(''.join(f).strip())
                if l == 0:
                    filename = old_filename
                    keep = True
            except IOError:
                filename = old_filename
                keep = True
        if filename.count('keep') > 0:
            keep = True
        aln = list(Fasta.load(filename, ''))[0]
        assert(len(aln) == 3)
        assert(len(aln[0][1]) == len(aln[1][1]) == len(aln[2][1]))
        X += aln[0][1]
        if keep:
            A += '.' * len(aln[0][1])
        else: 
            A += aln[1][1]
        Y += aln[2][1]
        X_name = aln[0][0]
        A_name = aln[1][0]
        Y_name = aln[2][0]
    Fasta.save([(X_name, X), (Y_name, Y), (A_name, A)], output_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('list_of_files')
    parser.add_argument('output')
    args = parser.parse_args()
    main(args.list_of_files, args.output)