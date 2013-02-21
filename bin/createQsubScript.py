import json
import argparse
import sys
from algorithm.Graphs import toposort

def Open(filename, mode):
    if filename == '-':
        if mode == 'w':
            return sys.stdout
        elif mode == 'r':
            return sys.stderr
        else: 
            sys.stderr.write('ERROR: Unknown mode "{0}"'.format(mode))
            exit(1)
    else:
        return open(filename, mode)

def main():
    parser = argparse.ArgumentParser(description='Run commands in gridengine')
    parser.add_argument('config', type=str, help="Config file")
    parser.add_argument('output', type=str, help="Output file")
    parsed_arg = parser.parse_args()
    
    with Open(parsed_arg.config) as f:
        config = json.load(f)
        
    graph = dict()
    for name, item in config.iteritems:
        graph[name] = [] if "depends" not in item else item.depends
    
    with Open(parsed_arg.output) as f:
        
        f.write('#!/bin/bash\n\n')
        
        for job in toposort(graph):
            item = config[job]
            param = ['-terse', '-cwd']
                    
            if "depends" in item:
                param.append('-hold_jid')
                param.append(','.join(['$' + x for x in item.depends]))
            
            if "array" in item:
                param.append('-t')
                assert(len(item.array) > 0 and len(item.array) < 4)
                param.append(
                    ''.join([
                        ''.join(x) 
                        for x in zip(map(str, item.array), ['-', ':', ''])
                    ])
                )
            
            if "resources" in item:
                assert(len(item.resources) > 0)
                param.append('-l')
                param.append(','.join([
                    '='.join(x) for x in item.resources.iteritems()
                ]))
            
            if "params" in item:
                assert(len(item.params) > 0)
                param.append(' '.join(item.params))
            
            query = '{jobname}=`qsub {parameters} {command}`'.format(
                jobname=job,
                parameters=' '.split(param),
                command=item.cmd
            )
            f.write(query + '\n')
        
    
    
    
if __name__ == "__main__":
    main()
