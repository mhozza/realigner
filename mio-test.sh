#!/bin/bash
export PYTHONPATH=./:$PYTHONPATH
PYTHON=/usr/bin/python
export SGE_TASK_FIRST=1
export SGE_TASK_ID=1
export SGE_TASK_LAST=10
export SGE_STEP_SIZE=1

time $PYTHON bin/Realign.py \
	--mathType LogNum \
	--beam_width 30 \
	--sequence_regexp $3 $4 \
	--algorithm viterbi\
	--model $5\
	--annotation_model ${1%.fa}.js\
	--draw $2.png\
	$1\
	$2
