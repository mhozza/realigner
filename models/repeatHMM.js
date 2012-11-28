{
	"__name__": "GeneralizedPairHMM",
	"transitions": [
	    {"from": "Match", "to": "Match", "prob": {"__name__": "trans", "key": "MM"}},
	    {"from": "Match", "to": "InsertX", "prob": {"__name__": "trans", "key": "MI"}},
	    {"from": "Match", "to": "InsertY", "prob": {"__name__": "trans", "key": "MI"}},
	    {"from": "Match", "to": "Repeat", "prob": {"__name__": "trans", "key": "MR"}},
	    {"from": "InsertX", "to": "Match", "prob": {"__name__": "trans", "key": "IM"}},
	    {"from": "InsertX", "to": "InsertX", "prob": {"__name__": "trans", "key": "II"}},
	    {"from": "InsertX", "to": "InsertY", "prob": {"__name__": "trans", "key": "II"}},
	    {"from": "InsertX", "to": "Repeat", "prob": {"__name__": "trans", "key": "IR"}},
	    {"from": "InsertY", "to": "Match", "prob": {"__name__": "trans", "key": "IM"}},
	    {"from": "InsertY", "to": "InsertX", "prob": {"__name__": "trans", "key": "II"}},
	    {"from": "InsertY", "to": "InsertY", "prob": {"__name__": "trans", "key": "II"}},
	    {"from": "InsertY", "to": "Repeat", "prob": {"__name__": "trans", "key": "IR"}},
	    {"from": "Repeat", "to": "Match", "prob": {"__name__": "trans", "key": "RM"}},
	    {"from": "Repeat", "to": "InsertX", "prob": {"__name__": "trans", "key": "RI"}},
	    {"from": "Repeat", "to": "InsertY", "prob": {"__name__": "trans", "key": "RI"}},
	    {"from": "Repeat", "to": "Repeat", "prob": {"__name__": "trans", "key": "RR"}}
	],
	"states": [
	    {
	    	"__name__": "GeneralizedPairState",
	    	"name": "Match",
	    	"startprob": 0.25,
	    	"endprob": 1.0,
	    	"durations": [[[1, 1], 1.0]],
	    	"emission": {
	    		"__name__": "JukesCantorGenerator",
	    		"alphabet": "ACGT",
	    		"time": 0.47
	    	}
	    	
	    },
	    {
	    	"__name__": "GeneralizedPairState",
	    	"name": "InsertX",
	    	"startprob": 0.25,
	    	"endprob": 1.0,
	    	"durations": [[[1, 0], 1.0]],
	    	"emission": {"__name__": "backgroundprob", "alphabet": "ACGT"}    	
	    },
	    {
	    	"__name__": "GeneralizedPairState",
	    	"name": "InsertY",
	    	"startprob": 0.25,
	    	"endprob": 1.0,
	    	"durations": [[[0, 1], 1.0]],
	    	"emission": {"__name__": "backgroundprob", "alphabet": "ACGT"}    	
	    },
	    {
	    	"__name__": "PairRepeatState", 
	    	"name": "Repeat",
	    	"startprob": 0.25,
	    	"endprob": 1.0,
	    	"durations": [],
	    	"emission": []
	    }
	]	
}