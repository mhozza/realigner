# pylint: disable=C0103, C0111, W0511
import argparse
from tools.file_wrapper import Open
import json
from alignment import Fasta


def main(files_filename, output_filename, suffix, base_dir):
    X = ""
    Y = ""
    A = ""
    with Open(output_filename, 'w') as ff:
        files = json.load(Open(files_filename))
        total = len(files)
        done = 0
        X_name = 'X'
        Y_name = 'Y'
        A_name = 'A'
        for filename in files:
            if done % 100 == 0:
                print '{}/{} {:.2}%'.format(done, total, 100.0 * done / total)
            if filename == "":
                Fasta.saveAlignmentPiece(
                    [
                        (X_name, X),
                        (Y_name, Y),
                        (A_name, A),
                    ],
                    ff,
                )
                X = ""
                Y = ""
                A = ""
                continue
            done += 1
            old_filename = filename
            keep = False
            
            if filename.count('keep') == 0:
                filename = filename[:-2] + suffix
                if base_dir != None:
                    filename = base_dir + '/' + filename.split('/')[-1]
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('list_of_files')
    parser.add_argument('output')
    parser.add_argument('suffix')
    parser.add_argument('base_dir', default=None)
    args = parser.parse_args()
    main(args.list_of_files, args.output, args.suffix, args.base_dir)
