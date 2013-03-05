#!/bin/bash

export PYTHONPATH=./

# Select sequences from alignment and split it into files, save as fasta
time pypy scripts/experiments/repeat000/SplitAlignment.py \
	data/alignments/calJac3mini.maf \
	working_dir_tmp \
	4 \
	output_file_from_split.txt \
	'calJac.*' \
	'rheMac.*'

# Compute statistics from input alignment
time pypy scripts/experiments/repeat000/PrepareParameters.py \
	output_file_from_split.txt \
	output_file_from_prepare.{index}.txt \
	--start 0 \
	--step 2
time pypy scripts/experiments/repeat000/PrepareParameters.py \
	output_file_from_split.txt \
	output_file_from_prepare.{index}.txt \
	--start 2 \
	--step 2

# Agregate statistics
time pypy scripts/experiments/repeat000/AggregateParameters.py \
	output_file_from_prepare.*.txt \
	working_dir_tmp/stat \
	output_file_from_aggregate.txt

# Create model
time python scripts/experiments/repeat000/CreateModel.py \
	data/models/repeatHMM.js \
	output_file_from_aggregate.txt \
	0.1 \
	output_file_from_create.txt
