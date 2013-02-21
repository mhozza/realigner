#!/bin/bash
PARALELISM=20
INPUT_ALIGNMENT='/projects/genomes/rheMac2/rheMac2.2bit'
INPUT_FILE=`basename $INPUT_ALIGNMENT`
INPUT_EXTENSION=`echo $INPUT_FILE | sed -e 's/^.*[.]\([^.]*\)$/\1/'`
INPUT_BASE=`basename $INPUT_FILE .$INPUT_EXTENSION`

if 

time twoBitToFa /projects/genomes/rheMac2/rheMac2.2bit data/alignments/rheMac2.fa
real    0m51.231s
user    0m14.345s
sys     0m5.104s

