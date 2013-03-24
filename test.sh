#!/Bin/bash

export PYTHONPATH=./ #\:/usr/lib/python2.7/dist-packages
PYTHON=pypy-env/bin/pypy
# Select sequences from alignment and split it into files, save as fasta

case 'nosample' in
		
'sample')
	
	time $PYTHON scripts/experiments/repeat000/SplitAlignment.py \
		data/alignments/7way-chr15.maf \
		working_dir_tmp \
		4 \
		output_file_from_split.txt \
		'hg19.*' \
		'canFam2.*'
	
# Compute statistics from input alignment
	time $PYTHON scripts/experiments/repeat000/PrepareParameters.py \
		output_file_from_split.txt \
		output_file_from_prepare.{index}.txt \
		--start 0 \
		--step 2
	time $PYTHON scripts/experiments/repeat000/PrepareParameters.py \
		output_file_from_split.txt \
		output_file_from_prepare.{index}.txt \
		--start 2 \
		--step 2
	
# Agregate statistics
	time $PYTHON scripts/experiments/repeat000/AggregateParameters.py \
		output_file_from_prepare.*.txt \
		working_dir_tmp/stat \
		output_file_from_aggregate.txt
	
# Create model
	time $PYTHON scripts/experiments/repeat000/CreateModel.py \
		data/models/repeatHMM.js \
		output_file_from_aggregate.txt \
		0.01 \
		output_file_from_create.txt

# Sample alignments
	time $PYTHON bin/Sample.py \
		working_dir_tmp/sampled_alignments/{id}.fa \
		1 \
		1000 \
		1000 \
		--output_files output_from_sample.txt \
		--model output_file_from_create.txt
	;&
*)	

	export SGE_TASK_FIRST=1
	export SGE_TASK_ID=1
	export SGE_TASK_LAST=10
	export SGE_STEP_SIZE=1
	
	time $PYTHON bin/Realign.py \
		working_dir_tmp/sampled_alignments/{id}.fa \
		working_dir_tmp/sampled_alignments/{id}.realigned.fa \
		--model output_file_from_create.txt \
		--mathType LogNum \
		--beam_width 30 \
		--repeat_width 0 \
		--sequence_regexp sequence1 sequence2 \
		--tracks original_repeats  \
		--intermediate_output_files 'posterior:table.js,viterbi:viterbi.js,viterbi_path:viterbi_path.js' #\
		#--intermediate_input_files 'posterior:table.js,viterbi:viterbi.js,viterbi_path:viterbi_path.js' 
				
	;&
esac
