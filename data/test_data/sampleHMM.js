[
	{
		"__name__": "State",
		"name" : "SimpleState",
		"emission" : [
			["A", 0.2],
			["C", 0.3],
			["G", 0.1],
			["T", 0.7]
		],
		"startprob": 1.0,
		"endprob": 1.0
	},
	
	{
		"__name__": "GeneralizedState",
		"name" : "GeneralState",
		"emission" : [
			["A", 0.2],
			["C", 0.3],
			["G", 0.1],
			["T", 0.7]
		],
		"durations" : [
		    [1,0.1],
		    [2,0.4],
		    [0,0.5]
		],
		"startprob": 1.0,
		"endprob": 1.0
	},
	
	{
		"__name__": "GeneralizedPairState",
		"name" : "GeneralPairState",
		"emission" : [
  			[["A", "C"], 0.2],
			[["C", "G"], 0.3],
			[["G", "A"], 0.1],
			[["T", "T"], 0.7]
		],
		"durations" : [
		    [[1,1], 0.1],
		    [[1,0], 0.4],
		    [[0,1], 0.5]
		],
		"startprob": 1.0,
		"endprob": 1.0
	},
	
	{
		"__name__": "HMM",
		"states": [
		    {
	    		"__name__": "State",
	    		"name" : "SimpleState",
	    		"emission" : [
	    			["A", 0.2],
	    			["C", 0.3],
	    			["G", 0.1],
	    			["T", 0.7]
	    		],
	    		"startprob": 1.0,
	    		"endprob": 1.0	
		    }
		],
		"transitions": [
		    {"from": "SimpleState", "to": "SimpleState", "prob": 1.0},
		    {"from": "SimpleState", "to": "SimpleState", "prob": 0.0}
		] 
	}
]