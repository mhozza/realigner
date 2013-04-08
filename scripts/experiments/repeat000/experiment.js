{
	"SplitAlignment": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"cmd": ["pypy-env/bin/pypy", 
			"scripts/experiments/repeat000/SplitAlignment.py",
			"/projects/ucsc-alignments/7way/chr15.maf.gz",
			"data/experiments/repeat0001/tmp",
			"400",
			"data/experiments/repeat0001/alnfiles_splitted.js",
			"'hg19.*'",
			"'canFam2.*'"]
	},
	"ComputeStatistics": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["SplitAlignment"],
		"array": [1, 400, 20],
		"cmd": ["pypy-env/bin/pypy",
			"scripts/experiments/repeat000/PrepareParameters.py",
			"data/experiments/repeat0001/alnfiles_splitted.js",
			"data/experiments/repeat0001/statistics.{index}.js",
			"--sequence_regexp 'hg19.*' 'canFam2.*'",
			"--alignment_regexp '\\.[0-9]*$'"]
	},
	"AggregateStatistics": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["ComputeStatistics"],
		"cmd": ["pypy-env/bin/pypy",
			"scripts/experiments/repeat000/AggregateParameters.py",
			"data/experiments/repeat0001/statistics.{1,21,41,61,81,101,121,141,161,181,201,221,241,261,281,301,321,341,361,381}.js",
			"data/experiments/repeat0001/stat",
			"data/experiments/repeat0001/aggregated_stats.js"]
	},	
	"CreateModel": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["AggregateStatistics"],
		"cmd": ["pypy-env/bin/pypy",
			"scripts/experiments/repeat000/CreateModel.py",
			"data/models/repeatHMM.js",
			"data/experiments/repeat0001/aggregated_stats.js",
			"data/experiments/repeat0001/model.js"]
	},
	"SampleAlignments": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["CreateModel"],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Sample.py",
			"data/experiments/repeat0001/sampled_aln/aln_{id}.fa",
			"100",
			"1000",
			"1000",
			"--output_files data/experiments/repeat0001/sampled_alignments.js",
			"--model data/experiments/repeat0001/model.js"]
	},
	"RunRepeatRealigner": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["SampleAlignments"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Realign.py",
			"data/experiments/repeat0001/sampled_aln/aln_{id}.fa",
			"data/experiments/repeat0001/sampled_aln/aln_{id}.repeatRealigner.fa",
			"--model data/experiments/repeat0001/model.js",
			"--mathType LogNum",
			"--beam_width 30",
			"--repeat_width 0",
			"--sequence_regexp 'sequence1' 'sequence2'",
			"--tracks trf"]
	},
	"RunRepeatRealignerOriginalRepeats": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["SampleAlignments"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Realign.py",
			"data/experiments/repeat0001/sampled_aln/aln_{id}.fa",
			"data/experiments/repeat0001/sampled_aln/aln_{id}.repeatRealignerOriginal.fa",
			"--model data/experiments/repeat0001/model.js",
			"--mathType LogNum",
			"--beam_width 30",
			"--repeat_width 0",
			"--sequence_regexp 'sequence1' 'sequence2'",
			"--tracks original_repeats"]
	},
	"RunViterbi": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["RunRepeatRealigner"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Realign.py",
			"data/experiments/repeat0001/sampled_aln/aln_{id}.fa",
			"data/experiments/repeat0001/sampled_aln/aln_{id}.viterbiRealigner.fa",
			"--model data/experiments/repeat0001/model.js",
			"--mathType LogNum",
			"--beam_width 30",
			"--repeat_width 0",
			"--sequence_regexp 'sequence1' 'sequence2'",
			"--tracks trf",
			"--algorithm viterbi"]
	},
	"RunViterbiOriginalRepeats": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["SampleAlignments"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Realign.py",
			"data/experiments/repeat0001/sampled_aln/aln_{id}.fa",
			"data/experiments/repeat0001/sampled_aln/aln_{id}.viterbiRealignerOriginal.fa",
			"--model data/experiments/repeat0001/model.js",
			"--mathType LogNum",
			"--beam_width 30",
			"--repeat_width 0",
			"--sequence_regexp 'sequence1' 'sequence2'",
			"--tracks original_repeats",
			"--algorithm viterbi"]
	}

}
