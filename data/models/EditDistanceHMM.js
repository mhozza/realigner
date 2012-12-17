{
	"__name__": "GeneralizedPairHMM",
	"transitions": [
	    {"from": "Match", "to": "Match", "prob": 1.0},
	    {"from": "Match", "to": "InsertX", "prob": 1.0},
	    {"from": "Match", "to": "InsertY", "prob": 1.0},
	    {"from": "InsertX", "to": "Match", "prob": 1.0},
	    {"from": "InsertX", "to": "InsertX", "prob": 1.0},
	    {"from": "InsertX", "to": "InsertY", "prob": 1.0},
	    {"from": "InsertY", "to": "Match", "prob": 1.0},
	    {"from": "InsertY", "to": "InsertX", "prob": 1.0},
	    {"from": "InsertY", "to": "InsertY", "prob": 1.0}
	],
	"states": [
	    {
	    	"__name__": "GeneralizedPairState",
	    	"name": "Match",
	    	"startprob": 1,
	    	"endprob": 1.0,
	    	"durations": [[[1, 1], 1.0]],
	    	"emission": [
	    	    [["A", "A"], 1.0],
	    	    [["A", "C"], 0.0],
	    	    [["A", "G"], 0.0],
	    	    [["A", "T"], 0.0],
	    	    [["C", "A"], 0.0],
	    	    [["C", "C"], 1.0],
	    	    [["C", "G"], 0.0],
	    	    [["C", "T"], 0.0],
	    	    [["G", "A"], 0.0],
	    	    [["G", "C"], 0.0],
	    	    [["G", "G"], 1.0],
	    	    [["G", "T"], 0.0],
	    	    [["T", "A"], 0.0],
	    	    [["T", "C"], 0.0],
	    	    [["T", "G"], 0.0],
	    	    [["T", "T"], 1.0]
	    	],
	    	"onechar": "M"
	    },
	    {
	    	"__name__": "GeneralizedPairState",
	    	"name": "InsertX",
	    	"startprob": 1.0,
	    	"endprob": 1.0,
	    	"durations": [[[1, 0], 1.0]],
	    	"emission": [
	    	    [["A", ""], 0.5],
	    	    [["C", ""], 0.5],
	    	    [["G", ""], 0.5],
	    	    [["T", ""], 0.5]
	    	],
	    	"onechar": "X"    	
	    },
	    {
	    	"__name__": "GeneralizedPairState",
	    	"name": "InsertY",
	    	"startprob": 1.0,
	    	"endprob": 1.0,
	    	"durations": [[[0, 1], 1.0]],
	    	"emission": [
	    		    	    [["", "A"], 0.5],
	    		    	    [["", "C"], 0.5],
	    		    	    [["", "G"], 0.5],
	    		    	    [["", "T"], 0.5]
	    		    	],
		    "onechar": "Y"    	
	    }
	]	
}