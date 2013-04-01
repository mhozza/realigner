#!/bin/bash

export PYTHONPATH=./ #\:/usr/lib/python2.7/dist-packages
PYTHON=/usr/bin/python
# Select sequences from alignment and split it into files, save as fasta
export SGE_TASK_FIRST=1
export SGE_TASK_ID=1
export SGE_TASK_LAST=10
export SGE_STEP_SIZE=1

time $PYTHON bin/Realign.py \
	data/sequences/simulated_alignment.fa\
	data/sequences/simulated_alignment.realigned.fa\
	--model data/models/ClassificationHMM.js\
	--mathType LogNum \
	--beam_width 30 \
	--sequence_regexp sequence1 sequence2 \
	--algorithm viterbi
				
	#working_dir_tmp/sampled_alignments/{id}.fa \
	#working_dir_tmp/sampled_alignments/{id}.realigned.fa \
