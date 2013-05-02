#!/bin/bash
set -e
if [ `uname -n` == 'panda-cub' ]; then 
        echo -e '\e[1;31mNa notebooku sa nespustim!'
        tput sgr0
        exit 1
fi

mkdir -p tmp

export PYTHONPATH=./ #\:/usr/lib/python2.7/dist-packages
PYTHON=pypy-env/bin/pypy
# Select sequences from alignment and split it into files, save as fasta

case 'nosample' in
		
'sample')
	
	time $PYTHON scripts/experiments/repeat000/SplitAlignment.py \
		data/alignments/7way-chr15.maf \
		working_dir_tmp \
		4 \
		tmp/output_file_from_split.txt \
		'hg19.*' \
		'canFam2.*'

# Compute statistics from input alignment
	time $PYTHON scripts/experiments/repeat000/PrepareParameters.py \
		tmp/output_file_from_split.txt \
		tmp/output_file_from_prepare.{index}.txt \
		--start 0 \
		--step 2 \
		--sequence_regexp 'hg19.*' 'canFam2.*' \
		--alignment_regexp '\.[0-9]*$'
	time $PYTHON scripts/experiments/repeat000/PrepareParameters.py \
		tmp/output_file_from_split.txt \
		tmp/output_file_from_prepare.{index}.txt \
		--start 2 \
		--step 2 \
		--sequence_regexp 'hg19.*' 'canFam2.*' \
		--alignment_regexp '\.[0-9]*$'

	
# Agregate statistics
	time $PYTHON scripts/experiments/repeat000/AggregateParameters.py \
		tmp/output_file_from_prepare.*.txt \
		working_dir_tmp/stat \
		tmp/output_file_from_aggregate.txt


# Create model
	time $PYTHON scripts/experiments/repeat000/CreateModel.py \
		data/models/repeatHMM.js \
		tmp/output_file_from_aggregate.txt \
		tmp/output_file_from_create.txt

# Sample alignments
	time $PYTHON bin/Sample.py \
		working_dir_tmp/sampled_alignments/{id}.fa \
		10 \
		1000 \
		1000 \
		--output_files tmp/output_from_sample.txt \
		--model tmp/output_file_from_create.txt


		;&
*)	

	export SGE_TASK_FIRST=1
	export SGE_TASK_ID=1
	export SGE_TASK_LAST=10
	export SGE_STEP_SIZE=1

	./track.sh > memory_profile.csv 2> /dev/null &

	time $PYTHON bin/Realign.py \
		working_dir_tmp/sampled_alignments/{id}.fa \
		working_dir_tmp/sampled_alignments/{id}.realigned.fa \
		--model tmp/output_file_from_create.txt \
		--mathType LogNum \
		--beam_width 30 \
		--repeat_width 0 \
		--sequence_regexp sequence1 sequence2 \
		--tracks original_repeats,trf  \
		--draw output.png \
		--intermediate_output_files 'posterior:tmp/table.js,viterbi:tmp/viterbi.js,viterbi_path:tmp/viterbi_path.js' #\
		#--intermediate_input_files 'posterior:tmp/table.js,viterbi:tmp/viterbi.js,viterbi_path:tmp/viterbi_path.js' 
	
	killall -9 track.sh
	wait
			
	;&
esac
