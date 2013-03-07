import argparse
from alignment import  Fasta
from alignment.Alignment import Alignment
from adapters.TRFDriver import TRFDriver
import os
from algorithm.aggregations import histogram
import json
from tools.file_wrapper import Open

def toList(s):
    return [s]


def get_annotation(sequence, seq_to_aln, repeats):
    annotation = ['?'] * len(sequence)
    for repeat in repeats:
        for x in range(seq_to_aln[repeat.start], seq_to_aln[repeat.end]):
            annotation[x] = 'R'
    return ''.join(annotation)
        

def compute_annotation_track(alns, repeats):
    for alignment in alns:
        # Ocakavame dvojrozmerne zarovnanie
        seq1 = alignment.sequences[0]
        name1 = alignment.names[0]
        ann1 = get_annotation(seq1, alignment.seq_to_aln[0], repeats[name1])
        
        seq2 = alignment.sequences[1]
        name2 = alignment.names[1]
        ann2 = get_annotation(seq2, alignment.seq_to_aln[1], repeats[name2])
        
        assert(len(seq1) == len(seq2))
        D = histogram(zip(ann1, ann2), str)
        yield D


def main(input_file, output_file, trf):
    
    # THIS IS ONLY GENERATOR!!!
    alns = (Alignment(a) 
            for a in Fasta.load(input_file, '[.][0-9]+$', Alignment))
    
    # 1. run trf, 
    for trf_executable in trf:
        if os.path.exists(trf_executable):  
            trf = TRFDriver(trf_executable)
            break
    repeats = trf.run(input_file)
    
    
    
    A = list(compute_annotation_track(alns, repeats))
    json.dump(A, Open(output_file, 'w'), indent=4)
    # 2. tam kde je trf zarovnane s niecim zaujimavim, dame repeat,
    # 3. Ostatne dame standardne
    # repeats je slovnik listov.
    # problem je ze nesedia dlzky, lebo v jednom subore je viac zarovnani

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Annotate alignment for training')
    parser.add_argument('input', type=str, help="Input file")
    parser.add_argument('output', type=str, help="Output file")
    parser.add_argument('--trf', type=toList, default=[
                               "/cygdrive/c/cygwin/bin/trf407b.dos.exe",
                               "C:\\cygwin\\bin\\trf407b.dos.exe",
                               "/home/mic/Vyskum/duplikacie/trf404.linux64",
                               "/home/mic/bin/trf404.linux64",
                               ], help="Location of tandem repeat finder binary")
    parsed_arg = parser.parse_args()
    main(
         parsed_arg.input,
         parsed_arg.output,
         parsed_arg.trf,
    )