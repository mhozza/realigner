from bin.Realign import worker, compute_annotations
from tools import perf
from tools.file_wrapper import Open
from alignment import Fasta
from alignment.Alignment import Alignment
import sys
from alignment.AlignmentIterator import AlignmentBeamGenerator
import json
from repeats.RepeatGenerator import RepeatGenerator
from collections import defaultdict
from algorithm.LogNum import LogNum

# aj tak potrebujem pridať nejaký "realigner", lebo tam potrebujem pridat vselijake dalsie data
# trenovatko si zoberie consenzus s hintov. Nebude to sice ciste, ale bude to funkcne.
# Este by sa dalo zistit pravdepodobnosti a podla toho to zarovnat. To je ale grc, ale asi to tak spravim:-(
def jsonize(inp):
    t = type(inp)
    if t == dict or t == defaultdict:
        output = list()
        for k, v in inp.iteritems():
            output.append((jsonize(k), jsonize(v)))
        return output
    elif t == list:
        output = []
        for x in inp:
            output.append(jsonize(x))
        return output
    elif t == type(LogNum()):
        return inp.value
    elif t == tuple:
        output = []
        for x in inp:
            output.append(jsonize(x))
        return tuple(output)
    return inp

def expectation_generator(args, model, alignment_filename, annotations):
    for aln in Fasta.load(
        alignment_filename, 
        args.alignment_regexp, 
        Alignment, 
        sequence_selectors=args.sequence_regexp):
        if len(aln.sequences) < 2:
            sys.stderr.write("ERROR: not enough sequences in file\n")
            raise "ERROR: not enough sequences in file"
        seq1, seq2 = tuple(map(Fasta.alnToSeq, aln.sequences[:2]))
        positionGenerator = list(
            AlignmentBeamGenerator(aln, args.beam_width)
        )
        
        RX = RepeatGenerator(None, args.repeat_width)
        RY = RepeatGenerator(None, args.repeat_width)
        for rt in ['trf', 'original_repeats']:
            if rt in annotations:
                RX.addRepeats(annotations[rt][aln.names[0]])
                RY.addRepeats(annotations[rt][aln.names[1]])
        RX.buildRepeatDatabase()
        RY.buildRepeatDatabase()
        if 'Repeat' in model.statenameToID:
            model.states[
                model.statenameToID['Repeat']
            ].addRepeatGenerator(RX, RY)
        
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
    annotations = compute_annotations(args, alignment_filename)
    with Open(output_filename, 'w') as fp:
        json.dump(jsonize(list(expectation_generator(args, model, 
                                                     alignment_filename,
                                                     annotations))),
                  fp ,indent=4)


if __name__ == "__main__":
    ret = worker(compute_expectations)
    perf.printAll()
    exit(ret)