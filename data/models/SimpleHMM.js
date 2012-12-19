{
	"__name__": "GeneralizedPairHMM",
	"transitions": [
	    {"from": "Match", "to": "Match", "prob": {"__name__": "trans", "key": "MM"}},
	    {"from": "Match", "to": "InsertX", "prob": {"__name__": "trans", "key": "MI"}},
	    {"from": "Match", "to": "InsertY", "prob": {"__name__": "trans", "key": "MI"}},
	    {"from": "InsertX", "to": "Match", "prob": {"__name__": "trans", "key": "IM"}},
	    {"from": "InsertX", "to": "InsertX", "prob": {"__name__": "trans", "key": "II"}},
	    {"from": "InsertX", "to": "InsertY", "prob": {"__name__": "trans", "key": "II"}},
	    {"from": "InsertY", "to": "Match", "prob": {"__name__": "trans", "key": "IM"}},
	    {"from": "InsertY", "to": "InsertX", "prob": {"__name__": "trans", "key": "II"}},
	    {"from": "InsertY", "to": "InsertY", "prob": {"__name__": "trans", "key": "II"}}
	],
	"states": [
	    {
	    	"__name__": "GeneralizedPairState",
	    	"name": "Match",
	    	"startprob": 0.33,
	    	"endprob": 1.0,
	    	"durations": [[[1, 1], 1.0]],
	    	"emission": {
	    		"__name__": "JukesCantorGenerator",
	    		"alphabet": "ACGT",
	    		"timeX": 0.01,
		    	"timeY": 0.04,
		        "backgroundprob": {"__name__": "backgroundprob", "alphabet": "ACGT"}
	    	},
	    	"onechar": "M"
	    },
	    {
	    	"__name__": "GeneralizedPairState",
	    	"name": "InsertX",
	    	"startprob": 0.33,
	    	"endprob": 1.0,
	    	"durations": [[[1, 0], 1.0]],
	    	"emission": {"__name__": "backgroundprob", "alphabet": "ACGT", 
	    		         "tracks": 2, "track": 0},
	    	"onechar": "X"    	
	    },
	    {
	    	"__name__": "GeneralizedPairState",
	    	"name": "InsertY",
	    	"startprob": 0.33,
	    	"endprob": 1.0,
	    	"durations": [[[0, 1], 1.0]],
	    	"emission": {"__name__": "backgroundprob", "alphabet": "ACGT", 
		                 "tracks": 2, "track": 1},
		    "onechar": "Y"    	
	    }
	]	
}