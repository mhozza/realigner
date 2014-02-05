#!/bin/bash

export PYTHONPATH=./ #\:/usr/lib/python2.7/dist-packages
PYTHON=/usr/bin/python
# Select sequences from alignment and split it into files, save as fasta
export SGE_TASK_FIRST=1
export SGE_TASK_ID=1
export SGE_TASK_LAST=10
export SGE_STEP_SIZE=1

time $PYTHON bin/Realign.py \
	--mathType LogNum \
	--beam_width 30 \
	--sequence_regexp $3 $4 \
	--algorithm viterbi\
    --model data/models/ClassificationHMM.js\
	$1\
	$2

	# --model data/models/OracleHMM.js\
	# --model data/models/SimpleHMM.js\
	# --draw $2.png\
	# working_dir_tmp/sampled_alignments/{id}.fa \
	# working_dir_tmp/sampled_alignments/{id}.realigned.fa \
