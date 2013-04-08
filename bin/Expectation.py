from bin.Realign import worker
from tools import perf
from tools.file_wrapper import Open
from alignment import Fasta
from alignment.Alignment import Alignment
import sys
from alignment.AlignmentIterator import AlignmentBeamGenerator
import json


def expectation_generator(args, model, alignment_filename):
    for aln in Fasta.load(
        alignment_filename, 
        args.alignment_regexp, 
        Alignment, 
        sequence_selectors=args.sequence_regexp):
        if len(aln.sequences) < 2:
            sys.stderr.write("ERROR: not enough sequences in file\n")
            return 1
        seq1, seq2 = tuple(map(Fasta.alnToSeq, aln.sequences[:2]))
        positionGenerator = list(
            AlignmentBeamGenerator(aln, args.beam_width)
        )
        (transitions, emissions), probability = model.getBaumWelchCounts(
            seq1, 0, len(seq1),
            seq2, 0, len(seq2),
            positionGenerator=positionGenerator
        )
        yield {
            "probability": probability,
            "transitions": transitions,
            "emissions": emissions,
        }


def compute_expectations(args, model, output_filename, alignment_filename):
    with Open(output_filename, 'w') as fp:
        json.dump(list(expectation_generator(args, model, alignment_filename)),
                  fp ,indent=4)


if __name__ == "__main__":
    ret = worker(compute_expectations)
    perf.printAll()
    exit(ret)