import json
import argparse
import os
from bin.AgregateAnnotation import main as AggregateAnnotation
from bin.AgregateTRFOutput import main as AggregateTRFOutput
from bin.TrfCover import main as TrfCover
from adapters.TRFDriver import TRFDriver
from adapters.TRFDriver import trf_paths
from tools.file_wrapper import Open
from tools import perf


@perf.runningTimeDecorator
def main(files, trf, alignment_regexp, sequence_regexp):
    output_files = {
        'emission': [],
        'transition': [],
        'trf_length': [],
        'trf_consensus': [],
        'trf_fulllength': [],
        'trf_cover': [],
    }
    for filename in files:
        # AggregateAnnotation
        em_file = filename + '.emission.stat'
        tr_file = filename + '.transition.stat'
        le_file = filename + '.trf_length.stat'
        co_file = filename + '.trf_consensus.stat'
        lef_file = filename + '.trf_fulllength.stat'
        cover_file = filename + '.trf_cover.stat'
        AggregateAnnotation(
            filename, 0, 1,
            em_file,
            tr_file
        )
        # Run TRF
        TRF = TRFDriver(trf)
        trf_output_filename = TRF.run(filename, dont_parse=True)
        # Aggregate TRF output
        AggregateTRFOutput(
            trf_output_filename,
            le_file,
            co_file,
            lef_file,
        )
        TrfCover(filename, cover_file, alignment_regexp, sequence_regexp, trf)
        output_files['emission'].append(em_file)
        output_files['transition'].append(tr_file)
        output_files['trf_length'].append(le_file)
        output_files['trf_consensus'].append(co_file)
        output_files['trf_fulllength'].append(co_file)
        output_files['trf_cover'].append(cover_file)
    return output_files


def toList(s):
    return [s]


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Prepare parameters')
    parser.add_argument('files', type=str, help='list_of_files')
    parser.add_argument('output_files', type=str, help='Output file')
    parser.add_argument('--start', type=int, default=0, 
                        help='Which files to select')
    parser.add_argument('--step', type=int, default=-1,
                        help='How many files to select (-1 to all)')
    parser.add_argument('--trf', type=toList, default=trf_paths
                        , help="Location of tandem repeat finder binary")
    parser.add_argument('--sequence_regexp', nargs='+', default=None,
                        help='Regular expressions used to select sequences.')
    parser.add_argument('--alignment_regexp', default='', 
                        help='Regular expression used to separate alignment' +
                        'in input file')

    parsed_arg = parser.parse_args()
    
    with Open(parsed_arg.files, 'r') as f:
        files = json.load(f)
        
    start = parsed_arg.start
    step = parsed_arg.step
    
    if step < 0:
        step = len(files)
    
    # Grid engine can always override parameters 
    if os.environ.has_key('SGE_TASK_ID'):
        start = int(os.environ['SGE_TASK_ID'])
    if os.environ.has_key('SGE_STEP_SIZE'):
        step = int(os.environ['SGE_STEP_SIZE'])
    output_files = main(files[start:start + step], parsed_arg.trf,
                        parsed_arg.alignment_regexp,
			parsed_arg.sequence_regexp)
    with Open(parsed_arg.output_files.format(index=start), 'w') as f:
        json.dump(output_files, f, indent=4)
    perf.printAll()
