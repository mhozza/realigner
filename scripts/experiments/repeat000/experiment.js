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
			"data/experiments/repeat0001/original_model.js"]
	},
	"SampleTrainData": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["CreateModel"],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Sample.py",
			"data/experiments/repeat0001/sampled_train_aln/aln_{id}.fa",
			"100",
			"1000",
			"1000",
			"--output_files data/experiments/repeat0001/sampled_train_alignments.js",
			"--model data/experiments/repeat0001/original_model.js"]
	},
	"SampleTestData": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["CreateModel"],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Sample.py",
			"data/experiments/repeat0001/sampled_test_aln/aln_{id}.fa",
			"100",
			"1000",
			"1000",
			"--output_files data/experiments/repeat0001/sampled_test_alignments.js",
			"--model data/experiments/repeat0001/original_model.js"]
	},
	"Expect_1": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["SampleTrainData"],
		"array": [1, 100],
		"cmd": [
		    "pypy-env/bin/pypy",
		    "bin/Expectation.py",
	        "data/experiments/repeat0001/sampled_train_aln/aln_{id}.fa",
	        "data/experiments/repeat0001/sampled_train_aln/aln_{id}.trained.1.js",
	        "--model data/experiments/repeat0001/original_model.js",
	        "--mathType LogNum",
	        "--beam_width 30",
	        "--repeat_width 0",
	        "--sequence_regexp sequence1 sequence2",
	        "-tracks trf"
	    ]
	},
	"Maximize_1": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["Expect_1"],
		"cmd": [
		    "pypy-env/bin/pypy",
		    "bin/Maximization.py",
	        "--model data/experiments/repeat0001/original_model.js",
	        "--output data/experiments/repeat0001/trained_model.1.js",
	        "--expectations data/experiments/repeat0001/sampled_train_aln/aln_{0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99}.trained.1.js",
		    "--mathType LogNum"
		]
	},	
	"Expect_2": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["Maximize_1"],
		"array": [1, 100],
		"cmd": [
		    "pypy-env/bin/pypy",
		    "bin/Expectation.py",
	        "data/experiments/repeat0001/sampled_train_aln/aln_{id}.fa",
	        "data/experiments/repeat0001/sampled_train_aln/aln_{id}.trained.2.js",
	        "--model data/experiments/repeat0001/trained_model.1.js",
	        "--mathType LogNum",
	        "--beam_width 30",
	        "--repeat_width 0",
	        "--sequence_regexp sequence1 sequence2",
	        "-tracks trf"
	    ]
	},
	"Maximize_2": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["Expect_2"],
		"cmd": [
		    "pypy-env/bin/pypy",
		    "bin/Maximization.py",
	        "--model data/experiments/repeat0001/trained_model.1.js",
	        "--output data/experiments/repeat0001/trained_model.2.js",
	        "--expectations data/experiments/repeat0001/sampled_train_aln/aln_{0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99}.trained.2.js",
		    "--mathType LogNum"
		]
	},
	"Expect_3": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["Maximize_2"],
		"array": [1, 100],
		"cmd": [
		    "pypy-env/bin/pypy",
		    "bin/Expectation.py",
	        "data/experiments/repeat0001/sampled_train_aln/aln_{id}.fa",
	        "data/experiments/repeat0001/sampled_train_aln/aln_{id}.trained.3.js",
	        "--model data/experiments/repeat0001/trained_model.2.js",
	        "--mathType LogNum",
	        "--beam_width 30",
	        "--repeat_width 0",
	        "--sequence_regexp sequence1 sequence2",
	        "-tracks trf"
	    ]
	},
	"Maximize_3": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["Expect_3"],
		"cmd": [
		    "pypy-env/bin/pypy",
		    "bin/Maximization.py",
	        "--model data/experiments/repeat0001/trained_model.2.js",
	        "--output data/experiments/repeat0001/trained_model.3.js",
	        "--expectations data/experiments/repeat0001/sampled_train_aln/aln_{0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99}.trained.3.js",
		    "--mathType LogNum"
		]
	},
	"Expect_4": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["Maximize_3"],
		"array": [1, 100],
		"cmd": [
		    "pypy-env/bin/pypy",
		    "bin/Expectation.py",
	        "data/experiments/repeat0001/sampled_train_aln/aln_{id}.fa",
	        "data/experiments/repeat0001/sampled_train_aln/aln_{id}.trained.4.js",
	        "--model data/experiments/repeat0001/trained_model.3.js",
	        "--mathType LogNum",
	        "--beam_width 30",
	        "--repeat_width 0",
	        "--sequence_regexp sequence1 sequence2",
	        "-tracks trf"
	    ]
	},
	"Maximize_4": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["Expect_3"],
		"cmd": [
		    "pypy-env/bin/pypy",
		    "bin/Maximization.py",
	        "--model data/experiments/repeat0001/trained_model.3.js",
	        "--output data/experiments/repeat0001/trained_model.4.js",
	        "--expectations data/experiments/repeat0001/sampled_train_aln/aln_{0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99}.trained.4.js",
		    "--mathType LogNum"
		]
	},
	"RunRepeatRealigner": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["SampleTestData", "Maximize_4"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Realign.py",
			"data/experiments/repeat0001/sampled_test_aln/aln_{id}.fa",
			"data/experiments/repeat0001/sampled_test_aln/aln_{id}.repeatRealigner.fa",
			"--model data/experiments/repeat0001/trained_model.4.js",
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
		"depends": ["SampleTestData", "Maximize_4"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Realign.py",
			"data/experiments/repeat0001/sampled_test_aln/aln_{id}.fa",
			"data/experiments/repeat0001/sampled_test_aln/aln_{id}.repeatRealignerOriginal.fa",
			"--model data/experiments/repeat0001/trained_model.4.js",
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
		"depends": ["SampleTestData", "RunRepeatRealigner", "Maximize_4"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Realign.py",
			"data/experiments/repeat0001/sampled_test_aln/aln_{id}.fa",
			"data/experiments/repeat0001/sampled_test_aln/aln_{id}.viterbiRealigner.fa",
			"--model data/experiments/repeat0001/trained_model.4.js",
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
		"depends": ["SampleTestData", "Maximize_4"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Realign.py",
			"data/experiments/repeat0001/sampled_test_aln/aln_{id}.fa",
			"data/experiments/repeat0001/sampled_test_aln/aln_{id}.viterbiRealignerOriginal.fa",
			"--model data/experiments/repeat0001/trained_model.4.js",
			"--mathType LogNum",
			"--beam_width 30",
			"--repeat_width 0",
			"--sequence_regexp 'sequence1' 'sequence2'",
			"--tracks original_repeats",
			"--algorithm viterbi"]
	}

}
