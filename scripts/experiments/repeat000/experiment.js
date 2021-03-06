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
	"CreateSimpleModel": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["AggregateStatistics"],
		"cmd": ["pypy-env/bin/pypy",
			"scripts/experiments/repeat000/CreateModel.py",
			"data/models/noRepeatHMM.js",
			"data/experiments/repeat0001/aggregated_stats.js",
			"data/experiments/repeat0001/original_simple_model.js",
                        "--simple_model True"]
	},
	"SampleTrainData": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["CreateModel"],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Sample.py",
			"data/experiments/repeat0001/sampled_train_short_aln/aln_{id}.fa",
			"100",
			"100",
			"100",
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
			"data/experiments/repeat0001/sampled_test_short_aln/orig_aln_{id}.fa",
			"100",
			"100",
			"100",
			"--output_files data/experiments/repeat0001/sampled_test_alignments.js",
			"--model data/experiments/repeat0001/original_model.js"]
	},
        "AlignWithMuscle": {
       		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["SampleTestData"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
                        "bin/MuscleAdapter.py",
                        "--input data/experiments/repeat0001/sampled_test_aln/orig_aln_{id}.fa",
                        "--output data/experiments/repeat0001/sampled_test_aln/aln_{id}.fa"
                       ]
        },
	"RunRepeatRealigner": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["AlignWithMuscle"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Realign.py",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.fa",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.repeatRealigner.fa",
			"--model data/experiments/repeat0001/original_model.js",
			"--mathType LogNum",
			"--beam_width 30",
			"--repeat_width 0",
			"--sequence_regexp 'sequence1' 'sequence2'",
			"--tracks trf"]
	},
	"RunSimpleModel": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["AlignWithMuscle", "CreateSimpleModel"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Realign.py",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.fa",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.simpleModel.fa",
			"--model data/experiments/repeat0001/original_simple_model.js",
			"--mathType LogNum",
			"--beam_width 30",
			"--sequence_regexp 'sequence1' 'sequence2'"
		       ]
	},
	"RunRepeatRealignerOriginalRepeats": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["AlignWithMuscle"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Realign.py",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.fa",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.repeatRealignerOriginal.fa",
			"--model data/experiments/repeat0001/original_model.js",
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
		"depends": ["AlignWithMuscle", "RunRepeatRealigner"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Realign.py",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.fa",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.viterbiRealigner.fa",
			"--model data/experiments/repeat0001/original_model.js",
			"--mathType LogNum",
			"--beam_width 30",
			"--repeat_width 0",
			"--sequence_regexp 'sequence1' 'sequence2'",
			"--tracks trf",
			"--algorithm viterbi"]
	},
	"RunViterbiSimpleModel": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["AlignWithMuscle", "CreateSimpleModel"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Realign.py",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.fa",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.simpleModelViterbi.fa",
			"--model data/experiments/repeat0001/original_simple_model.js",
			"--mathType LogNum",
			"--beam_width 30",
			"--sequence_regexp 'sequence1' 'sequence2'",
			"--algorithm viterbi"]
	},
	"RunViterbiOriginalRepeats": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["AlignWithMuscle"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Realign.py",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.fa",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.viterbiRealignerOriginal.fa",
			"--model data/experiments/repeat0001/original_model.js",
			"--mathType LogNum",
			"--beam_width 30",
			"--repeat_width 0",
			"--sequence_regexp 'sequence1' 'sequence2'",
			"--tracks original_repeats",
			"--algorithm viterbi"]
	},
        "PrepareTrainingDataForContextSoftware": {
                "params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["SampleTrainData"],
		"cmd": ["pypy-env/bin/pypy",
                        "bin/SplitAlignmentForContext.py",
                        "--alignment data/experiments/repeat0001/sampled_train_short_aln/aln_*.fa",
                        "--output data/experiments/repeat0001/sampled_train_short_aln/context_data.txt",
                        "--min_split_size 50",
                        "--max_split_size 75"
                       ]
        },
        "PrepareTestingDataForContextSoftware": {
                "params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["SampleTrainData"],
		"cmd": ["pypy-env/bin/pypy",
                        "bin/SplitAlignmentForContext.py",
                        "--alignment data/experiments/repeat0001/sampled_test_short_aln/aln_*.fa",
                        "--output data/experiments/repeat0001/sampled_test_short_aln/context_data.txt",
                        "--min_split_size 50",
                        "--max_split_size 75"
                       ]
        },
        "TrainContextSoftware": {
                "params": ["-v", "PYTHONPATH=./", "-b y"],
                        "stdout": "output",
                        "stderr": "output",
                        "depends": ["PrepareTrainingDataForContextSoftware"],
                        "cmd": [
                                "../Context/bin/train",
                                "infile=data/experiments/repeat0001/sampled_train_short_aln/context_data.txt",
                                "fpout=data/experiments/repeat0001/context_trained_model.txt",
                                "win=10"
                               ]
        },
        "RunContext": {
                "params": ["-v", "PYTHONPATH=./", "-b y"],
                "stdout": "output",
                "stderr": "output",
                "depends": ["TrainContextSoftware"],
                "array": [1, 100],
                "cmd": ["pypy-env/bin/pypy",
                        "bin/ContextSoftwareWrapper.py",
                        "--binary ../Context/bin/align",
                        "--input_template data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.fa",
                        "--output_template data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.context.fa",
                        "--model data/experiments/repeat0001/context_trained_model.txt",
                        "--window 10"
                       ]
        },
	"RunRepeatRealignerV2": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["AlignWithMuscle", "RunRepeatRealigner"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Realign.py",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.fa",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.repeatRealignerV2.fa",
			"--model data/experiments/repeat0001/original_model.js",
			"--mathType LogNum",
			"--beam_width 30",
			"--repeat_width 0",
			"--sequence_regexp 'sequence1' 'sequence2'",
			"--tracks trf",
                        "--ignore_states True"]
	},
        "RunRepeatRealignerOriginalRepeatsV2": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["AlignWithMuscle"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Realign.py",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.fa",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.repeatRealignerOriginalV2.fa",
			"--model data/experiments/repeat0001/original_model.js",
			"--mathType LogNum",
			"--beam_width 30",
			"--repeat_width 0",
			"--sequence_regexp 'sequence1' 'sequence2'",
			"--tracks original_repeats",
                        "--ignore_states True"]
	},
	"RunRepeatRealignerLotOfRepeats": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["AlignWithMuscle", "RunRepeatRealigner"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Realign.py",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.fa",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.repeatRealignerLotOfRepeats.fa",
			"--model data/experiments/repeat0001/original_model.js",
			"--mathType LogNum",
			"--beam_width 30",
			"--repeat_width 3",
			"--sequence_regexp 'sequence1' 'sequence2'",
			"--tracks trf",
                        "--ignore_states True"]
	},
	"RunRepeatRealignerFullV2": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["AlignWithMuscle", "RunRepeatRealigner"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Realign.py",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.fa",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.repeatRealignerFullV2.fa",
			"--model data/experiments/repeat0001/original_model.js",
			"--mathType float",
			"--beam_width 30",
			"--repeat_width 0",
			"--sequence_regexp 'sequence1' 'sequence2'",
			"--tracks trf_cons",
                        "-l memory 20G",
                        "--cons_count 0",
                        "--resolve_indels True",
                        "--ignore_states True"]
	},
	"RunRepeatRealignerFull": {
		"params": ["-v", "PYTHONPATH=./", "-b y"],
		"stdout": "output",
		"stderr": "output",
		"depends": ["AlignWithMuscle", "RunRepeatRealigner"],
		"array": [1, 100],
		"cmd": ["pypy-env/bin/pypy",
			"bin/Realign.py",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.fa",
			"data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.repeatRealignerFullV2.fa",
			"--model data/experiments/repeat0001/original_model.js",
			"--mathType float",
			"--beam_width 30",
			"--repeat_width 0",
			"--sequence_regexp 'sequence1' 'sequence2'",
			"--tracks trf_cons",
                        "-l memory 20G",
                        "--cons_count 0",
                        "--resolve_indels True",
                        "--ignore_states False"]
	},
        "EvaluateExperiment": {
                "params": ["-v", "PYTHONPATH=./", "-b y"],
                "stdout": "output",
                "stderr": "output",
                "depends": ["RunRepeatRealigner", "RunSimpleModel", "RunRepeatRealignerOriginalRepeats", "RunViterbi", "RunViterbiSimpleModel", "RunViterbiOriginalRepeats", "RunContext", "RunRepeatRealignerV2", "RunRepeatRealignerOriginalRepeatsV2", "RunRepeatRealignerLotOfRepeats", "RunRepeatRealignerFull", "RunRepeatRealignerFullV2"],
                "cmd": ["pypy-env/bin/pypy",
                        "bin/GetResultsFromExperiment.py",
                        "--correct data/experiments/repeat0001/sampled_test_short_aln/orig_aln_{id}.fa",
                        "--aln data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.{type}.fa",
                        "--part_output data/experiments/repeat0001/sampled_test_short_aln/aln_{id}.{type}.evaluated.js",
                        "--interval 1 100",
                        "--output data/experiments/repeat0001/{type}.evaluated.js",
                        "--types context repeatRealigner repeatRealignerOriginal simpleModel",
                                "simpleModelViterbi viterbiRealigner viterbiRealignerOriginal repeatRealignerLotOfRepeats RunRepeatRealignerFull RunRepeatRealignerFullV2"
                       ]
        }
}
