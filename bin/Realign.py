from algorithm.LogNum import LogNum
from hmm.HMMLoader import HMMLoader
from alignment import Fasta
from adapters.TRFDriver import TRFDriver
from alignment.AlignmentIterator import AlignmentBeamGenerator
from repeats.RepeatRealigner import RepeatRealigner
from tools import perf
import os   
import argparse

    
def getMathType(s):
    if s == 'LogNum':
        return LogNum
    elif s == 'float':
        return float
    else:
        raise('Unknown type')
    
def toList(s):
    return [s]


def getRealigner(s):
    if s == 'repeat':
        return RepeatRealigner
    else:
        raise('Unknown type')


@perf.runningTimeDecorator
def main():
    
    parser = argparse.ArgumentParser(description='Realign sequence using ' + 
                                     'informations from repeat realigner')
    parser.add_argument('--mathType', '-m', type=getMathType, default=float,
                        choices=[LogNum, float])
    parser.add_argument('alignment', type=str)
    parser.add_argument('output', type=str)
    parser.add_argument('--model', '-M', type=str,
                        default='data/models/repeatHMM.js')
    parser.add_argument('--trf', '-t', type=toList, default=[
                           "/cygdrive/c/cygwin/bin/trf407b.dos.exe",
                           "C:\\cygwin\\bin\\trf407b.dos.exe",
                           "/home/mic/Vyskum/duplikacie/trf404.linux64",
                           "/home/mic/bin/trf404.linux64",
                           ])
    parser.add_argument('--algorithm', "-a", type=getRealigner, 
                        default=RepeatRealigner, choices=[RepeatRealigner])
    parsed_arg = parser.parse_args()
    mathType = parsed_arg.mathType
    
        
    # Parse input parameters
    alignment_filename = parsed_arg.alignment
    output_filename = parsed_arg.output

    # Load model
    loader = HMMLoader(mathType) 
    model_filename = parsed_arg.model
    #model_filename = "data/models/EditDistanceHMM.js"
    #model_filename = "data/models/SimpleHMM.js"
    
    PHMM = loader.load(model_filename)["model"]

    # Load alignment
    aln = Fasta.load(alignment_filename)
    if len(aln.sequences) < 2:
        print("ERROR: not enough sequences in file")
        
    # Sequence 1
    seq1 = Fasta.alnToSeq(aln.sequences[0])
    seq1_length = len(seq1)
    seq1_name = aln.names[0]
    
    # Sequence 2
    seq2 = Fasta.alnToSeq(aln.sequences[1])
    seq2_length = len(seq2)
    seq2_name = aln.names[1]
    
    perf.msg("Data loaded in {time} seconds.")
    perf.replace()
    
    #TODO: some better way how to cope with additional information
    # Compute repeat hints
    for trf_executable in parsed_arg.trf:
        if os.path.exists(trf_executable):
            trf = TRFDriver(trf_executable, mathType=mathType)
            break
        
    repeats = trf.run(alignment_filename)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
    seq1_repeats = repeats[seq1_name]
    seq2_repeats = repeats[seq2_name]
    
    
    realigner = parsed_arg.algorithm()
    realigner.prepareData(PHMM, seq1_repeats, seq2_repeats)
    
    
    # positions
    positionGenerator = \
        list(AlignmentBeamGenerator(aln, width = 10))
    
    perf.msg("Hints computed in {time} seconds.")
    perf.replace()
    
    # Compute stuff
    table = PHMM.getPosteriorTable(seq1, 0, seq1_length, seq2, 0, seq2_length,
                                   positionGenerator = positionGenerator)
    
    perf.msg("Posterior table computed in {time} seconds.")
    perf.replace()
    
    aln = ""
    aln = realigner.realign(
        seq1_name, seq1, 0, seq1_length,
        seq2_name, seq2, 0, seq2_length,
        table,
        PHMM,
        positionGenerator,
        mathType=mathType
    )
    
    perf.msg("Sequence was realigned in {time} seconds.")
    perf.replace()
    
    # Save output
    Fasta.save(aln, output_filename)
    perf.msg("Output saved in {time} seconds.")

    
if __name__ == "__main__":
    main()
    perf.printAll()
    