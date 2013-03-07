import argparse
import json
from collections import defaultdict 

def _aggregate(dicts):
    output = defaultdict(int)
    for item in dicts:
        for key, value in item.iteritems():
            output[key] += value
    return output         
            

def __loadJSON(filename):
    with open(filename, 'r') as f:
        return json.load(f)            


def aggregate(filelist):
    output = dict()
    for tp, files in filelist.iteritems():
        output[tp] = _aggregate(map(__loadJSON, files))
    return output


def main(filelist_filenames, output_filebase, filelist_output):
    filelist = defaultdict(list)
    for filelist_filename in filelist_filenames:
        with open(filelist_filename, 'r') as f:
            files = json.load(f)
        for key, value in files.iteritems():
            filelist[key].extend(value)

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
    parser.add_argument('filelist', type=str, nargs='+',
                        help='Program input -- list of files')
    parser.add_argument('output', type=str, help='Base name for statistics')
    parser.add_argument('filelist_output', type=str,
                        help='Output file for filelist')
    parsed_arg = parser.parse_args()
    print(parsed_arg)
    main(
         parsed_arg.filelist,
         parsed_arg.output,
         parsed_arg.filelist_output
    ) 