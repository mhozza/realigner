import argparse
from alignment import  Fasta
from alignment.Alignment import Alignment
from adapters.TRFDriver import TRFDriver
import os

def toList(s):
    return [s]

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

aln = Alignment(Fasta.load(parsed_arg.input))

# 1. run trf, 
# 2. tam kde je trf zarovnane s niecim zaujimavim, dame repeat,
# 3. Ostatne dame standardne
for trf_executable in parsed_arg.trf:
        if os.path.exists(trf_executable):
            trf = TRFDriver(trf_executable)
            break

repeats = trf.run(parsed_arg.input)
# repeats je slovnik listov.



                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       




