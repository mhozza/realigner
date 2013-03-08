{
	"SplitAlignment": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"cmd": "/usr/bin/pypy scripts/experiments/repeat000/SplitAlignment.py data/alignments/calJac3mini.maf data/experiments/repeat0001/tmp 400 data/experiments/repeat0001/alnfiles_splitted.js 'calJac.*' 'rheMac.*'"			
	},
	"ComputeStatistics": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"depends": ["SplitAlignment"],
		"array": [1, 400, 20],
		"cmd": "/usr/bin/pypy scripts/experiments/repeat000/PrepareParameters.py data/experiments/repeat0001/alnfiles_splitted.js data/experiments/repeat0001/statistics.{index}.js"		
	},
	"AggregateStatistics": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"depends": ["ComputeStatistics"],
		"cmd": "/usr/bin/pypy scripts/experiments/repeat000/AggregateParameters.py data/experiments/repeat0001/statistics.{1,21,41,61,81,101,121,141,161,181,201,221,241,261,281,301,321,341,361,381}.js data/experiments/repeat0001/stat data/experiments/repeat0001/aggregated_stats.js"
	},	
	"CreateModel": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"depends": ["AggregateStatistics"],
		"cmd": "/usr/bin/pypy scripts/experiments/repeat000/CreateModel.py data/models/repeatHMM.js data/experiments/repeat0001/aggregated_stats.js 0.001 data/experiments/repeat0001/model.js"
	},
	"SampleAlignments": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"depends": ["CreateModel"],
		"cmd": "/usr/bin/pypy bin/Sample.py data/experiments/repeat0001/sampled_aln/aln_{id}.fa 100 1000 1000 --output_files data/experiments/repeat0001/sampled_alignments.js --model data/experiments/repeat0001/model.js"
	}
}