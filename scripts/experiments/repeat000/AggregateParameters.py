import argparse
import json
from collections import defaultdict

def _aggregate(dicts):
    output = defaultdict(int)
    for item in dicts:
        for key, value in item:
            output[key] += value
    return output         
            

def aggregate(filelist):
    output = dict()
    for tp, files in filelist.iteritems:
        f = [open(x, 'r') for x in files]
        output[tp] = _aggregate(map(json.load, f))
        map(lambda x:x.close(), f)
    return output


def main(filelist_filename, output_filebase, filelist_output):
    with open(filelist_filename, 'r') as f:
        filelist = json.load(f)
        
    files = list()
    for key, stat in aggregate(filelist).iteritems():
        output_filename = '{base}.{type}.stat'.format(base=output_filebase, 
                                                      type=key)
        with open(output_filename, 'w') as f:
            json.dump(stat, f, indent=4)
        files.append(output_filename)
            
    with open(filelist_output, 'w') as f:
        json.dump(files, f, indent=4)


if __name__ == "__main__":    
    parser = \
        argparse.ArgumentParser(description='Aggregate various statistics.')
    parser.add_argument('filelist', type=str,
                        help='Program input -- list of files')
    parser.add_argument('output', type=str, help='Base name for statistics')
    parser.add_argument('filelist_output', type=str,
                        help='Output file for filelist')
    parsed_arg = parser.parse_args()
    main(
         parsed_arg.filelist,
         parsed_arg.output,
         parsed_arg.filelist_output
    ) 