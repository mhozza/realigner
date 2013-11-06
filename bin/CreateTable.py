import argparse
from tools.file_wrapper import Open
import json
import re

def main(files, columns, headers, ignore):
    r = re.compile("^.*/([^/.]*)[.]evaluated.js$")
    out = []
    x = ['type']
    if headers == None:
        x.extend(columns)
    else:
        x.extend(headers)
        x.extend(columns[len(headers):])
    out.append(x);
    columns = map(lambda x: x.split(':'), columns)
    for filename in files:
        with Open(filename, 'r') as f: 
            data = json.load(f)
        rr = r.match(filename)
        if rr == None:
            row = [filename]
        else:
            row = [rr.group(1)]
        if row[0] in ignore:
            continue
        for column in columns:
            sel = data
            for key in column:
                if isinstance(sel, list):
                    key = int(key)
                sel = sel[key]
            row.append(sel)
        out.append(row)
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Extract tables from jsons.')
    parser.add_argument('--files', required=True, type=str, nargs='+',
                        help='Input jsons.')
    parser.add_argument('--columns', required=True, type=str, nargs='+',
                        help='Lists of colon separated nested selectors.')
    parser.add_argument('--headers', required=False, type=str, nargs='+',
                        help='Optional list of headers')
    parser.add_argument('--ignore', required=False, type=str, nargs='+',
                        help='Which types to ignore')
    args = parser.parse_args()
    if args.ignore == None:
        args.ignore = set()
    else:
        args.ignore = set(args.ignore)
    lines = main(args.files, args.columns, args.headers, args.ignore)
    maxLen = max([len(line[0]) for line in lines])
    for line in lines:
        line[0] = ("{{:{}}}".format(maxLen)).format(line[0])
        print '\t'.join(map(str, line))
