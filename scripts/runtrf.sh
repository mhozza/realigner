#!/bin/bash

export PYTHONPATH=./

for i in `seq $1 $2`; do 
        pypy bin/RunTRF.py $3$i.fa $3$i.fa.trf.json
done

base=`dirname $3`

for i in `seq 0 199`; do 
        cp $base/orig_aln_$i.fa.repeats $base/sampled_test_short_aln/aln_$i.fa.repeats; 
done
