import json
import argparse
from algorithm.Graphs import toposort
from tools.file_wrapper import Open
from tools import perf

# TODO: Pridaj moznost preskocit niektore casti -- ak su uz hotove

def cmd_to_string(cmd):
    if type(cmd) == list:
        return ' '.join(cmd)
    return cmd

@perf.runningTimeDecorator
def main(config_file, output_file):
    
    
    with Open(config_file, 'r') as f:
        config = json.load(f)
        
    graph = dict()
    for name, item in config.iteritems():
        graph[name] = [] if "depends" not in item else item['depends']
    
    with Open(output_file, 'w') as f:
        
        f.write('#!/bin/bash\n\n')
        for job in toposort(graph):
            item = config[job]
            param = ['-terse', '-cwd']
                    
            if "depends" in item:
                param.append('-hold_jid')
                param.append(','.join(['$' + x for x in item['depends']]))
            
            if "array" in item:
                param.append('-t')
                assert(len(item['array']) > 0 and len(item['array']) < 4)
                param.append(
                    ''.join([
                        ''.join(x) 
                        for x in zip(['', '-', ':'], map(str, item['array']))
                    ])
                )
            if 'stdout' in item:
                param.append('-o')
                param.append("'{}'".format(item['stdout']))
            if 'stderr' in item:
                param.append('-e')
                param.append("'{}'".format(item['stderr']))
            if "resources" in item:
                assert(len(item['resources']) > 0)
                param.append('-l')
                param.append(','.join([
                    '='.join(x) for x in item['resources'].iteritems()
                ]))
            
            if "params" in item:
                assert(len(item['params']) > 0)
                param.append(' '.join(item['params']))
            query = ("{jobname}=`qsub -N '{name}' {parameters} {command} " + \
                "| sed -e 's/[.].*$//'`").format(
                name=job,
                jobname=job,
                parameters=' '.join(param),
                command=cmd_to_string(item['cmd'])
            )
            f.write(query + '\n')

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run commands in gridengine')
    parser.add_argument('config', type=str, help="Config file")
    parser.add_argument('output', type=str, help="Output file")
    parsed_arg = parser.parse_args()
    main(parsed_arg.config, parsed_arg.output)
    perf.printAll()
