,
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
	        "--tracks trf"
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
	        "--tracks trf"
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
	        "--tracks trf"
	    ]
	},
	"Maximize_4": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["Expect_4"],
		"cmd": [
		    "pypy-env/bin/pypy",
		    "bin/Maximization.py",
	        "--model data/experiments/repeat0001/trained_model.3.js",
	        "--output data/experiments/repeat0001/trained_model.4.js",
	        "--expectations data/experiments/repeat0001/sampled_train_aln/aln_{0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99}.trained.4.js",
		    "--mathType LogNum"
		]
	},
