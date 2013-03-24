#!/Bin/bash

export PYTHONPATH=./ #\:/usr/lib/python2.7/dist-packages
PYTHON=pypy-env/bin/pypy
# Select sequences from alignment and split it into files, save as fasta
export SGE_TASK_FIRST=1
export SGE_TASK_ID=1
export SGE_TASK_LAST=10
export SGE_STEP_SIZE=1

time $PYTHON bin/Realign.py \
	working_dir_tmp/sampled_alignments/{id}.fa \
	working_dir_tmp/sampled_alignments/{id}.realigned.fa \
	--model data/models/SimpleHMM.js\
	--mathType LogNum \
	--beam_width 30 \
	--sequence_regexp sequence1 sequence2 \
	--algorithm viterbi
				
