{
	"SplitAlignment": {
		"params": ["-v", "PYTHONPATH=./"],
		"cmd": "/usr/bin/pypy scripts/experiments/repeat000/SplitAlignment.py data/alignments/calJac3mini.maf data/experiments/repeat0001/tmp 400 data/experiments/repeat0001/alnfiles_splitted.js 'calJac.*' 'rheMac.*'"			
	},
	"ComputeStatistics": {
		"params": ["-v", "PYTHONPATH=./"],
		"depends": ["SplitAlignment"],
		"array": [0, 400, 20],
		"cmd": "/usr/bin/pypy scripts/experiments/repeat000/PrepareParameters.py data/experiments/repeat0001/alnfiles_splitted.js data/experiments/repeat0001/statistics.{index}.js"		
	},
	"AggregateStatistics": {
		"params": ["-v", "PYTHONPATH=./"],
		"depends": ["ComputeStatistics"],
		"cmd": "/usr/bin/pypy scripts/experiments/repeat000/AggregateParameters.py data/experiments/repeat0001/statistics.{0,20,40,60,80,100,120,140,160,180,200,220,240,260,280,300,320,340,360,380}.js data/experiments/repeat0001/stat data/experiments/repeat0001/aggregated_stats.js"
	},	
	"CreateModel": {
		"params": ["-v", "PYTHONPATH=./"],
		"depends": ["AggregateStatistics"],
		"cmd": "/usr/bin/pypy scripts/experiments/repeat000/CreateModel.py data/models/repeatHMM.js data/experiments/repeat0001/aggregated_stats.js 0.1 data/experiments/repeat0001/model.js"
	}
	
}
