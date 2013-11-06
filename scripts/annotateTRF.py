import argparse
from adapters.TRFDriver import TRFDriver, trf_paths
from alignment.Alignment import Alignment
from alignment import Fasta
from tools import perf
import os
from collections import defaultdict


@perf.runningTimeDecorator
def main(input_file, output_file):

    for trf_executable in trf_paths:
        if os.path.exists(trf_executable):
            trf = TRFDriver(trf_executable)
            #break
    if not trf:
        raise "No trf found"
    repeats = trf.run(input_file)

    with open(output_file, 'w') as f:
        for alignment in Fasta.load(input_file, '\.[0-9]*$', Alignment):
            if len(alignment.sequences) != 2:
                print 'error'
                continue
            #print alignment.names
            annotation = list('.' * len(alignment.sequences[0]))
            annotationX = list('.' * len(alignment.sequences[0]))
            annotationY = list('.' * len(alignment.sequences[0]))
            trf = None
            for seq_name in alignment.names:
                index = None
                for i in range(len(alignment.names)):
                    if seq_name == alignment.names[i]:
                        index = i
                translator = alignment.seq_to_aln[index]
                revtranslator = alignment.aln_to_seq[index]
                for repeat in repeats[seq_name]:
                    for i in range(translator[repeat.start], translator[repeat.end]):
                        annotation[i] = 'R'
                        j = i - translator[repeat.start]
                        if index == 0:
                            annotationX[i] = repeat.consensus[revtranslator[j] % len(repeat.consensus)]
                        else:
                            annotationY[i] = repeat.consensus[revtranslator[j] % len(repeat.consensus)]
            d = defaultdict(int)
            ll = 0
            for v in annotation:
                if v != 'R':
                    if ll > 0:
                        d[ll] += 1
                        ll = 0
                else:  
                    ll += 1
            #for x, y in sorted(d.iteritems(), key=lambda x: x[1]):
            #    print '{}: {}'.format(x, y)
            #if len(d.keys()) > 0:
            #    print('Number of repeats: {}, average length: {}, maximum length: {}, minimum length: {}'.format(
            #        sum(d.values()),
            #        sum([x * y for x, y in d.iteritems()])/ max(sum(d.values()), 1),
            #        max(d.keys()),
            #        min(d.keys())
            #    ))

            seqX = alignment.sequences

            nm = alignment.names[0]
            aln = [(alignment.names[0], alignment.sequences[0].replace('.', '-')), 
                   ('consensusX' + nm, ''.join(annotationX)),
                   ('annotation' + nm, ''.join(annotation)),
                   ('consensusY' + nm, ''.join(annotationY)),
                   (alignment.names[1], alignment.sequences[1].replace('.','-'))]
            Fasta.saveAlignmentPiece(aln, f, -1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('output')
    args = parser.parse_args()
    main(args.input, args.output)
