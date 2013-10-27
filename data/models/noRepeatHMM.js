{
    "contants": [
 	    {
 	        "__name__": "@trans?",   	 
	        "MM": 0.94,
	        "MX": 0.03,
	        "MY": 0.03,
	        "XM": 0.94,
	        "YM": 0.94,
	        "XX": 0.03,
	        "XY": 0.03,
	        "YY": 0.03,
	        "YX": 0.03
        },
        {
        	"__name__": "@times?",
        	"jukes-cantor-pair-state-time-X": 0.00005,
        	"jukes-cantor-pair-state-time-Y": 0.00005
        },
        {
        	"__name__": "@background-probability?",
        	"value": [["A", 0.25], ["C", 0.25], ["G", 0.25], ["T", 0.25]]
        },
        {
        	"__name__": "@MatchStateEmissions?",
        	"value": {
	    		"__name__": "JukesCantorGenerator",
	    		"alphabet": "ACGT",
	    		"timeX": {"__name__": "times", "key": "jukes-cantor-pair-state-time-X"},
	    		"timeY": {"__name__": "times", "key": "jukes-cantor-pair-state-time-Y"},
	        	"backgroundprob": {"__name__": "background-probability", "key": "value"}
	    	}
        }
    ],
 	"model": {
 		"__name__": "GeneralizedPairHMM",
 		"transitions": [
 		    {"from": "Match", "to": "Match", "prob": {"__name__": "trans", "key": "MM"}},
 		    {"from": "Match", "to": "InsertX", "prob": {"__name__": "trans", "key": "MX"}},
 		    {"from": "Match", "to": "InsertY", "prob": {"__name__": "trans", "key": "MY"}},
 		    {"from": "InsertX", "to": "Match", "prob": {"__name__": "trans", "key": "XM"}},
 		    {"from": "InsertX", "to": "InsertX", "prob": {"__name__": "trans", "key": "XX"}},
 		    {"from": "InsertX", "to": "InsertY", "prob": {"__name__": "trans", "key": "XY"}},
 		    {"from": "InsertY", "to": "Match", "prob": {"__name__": "trans", "key": "YM"}},
 		    {"from": "InsertY", "to": "InsertX", "prob": {"__name__": "trans", "key": "YX"}},
 		    {"from": "InsertY", "to": "InsertY", "prob": {"__name__": "trans", "key": "YY"}}
 		],
 		"states": [
 		    {
 		    	"__name__": "GeneralizedPairState",
 		    	"name": "Match",
 		    	"startprob": 0.25,
 		    	"endprob": 1.0,
 		    	"durations": [[[1, 1], 1.0]],
 		    	"emission": {"__name__": "MatchStateEmissions", "key": "value"},
 		    	"onechar": "M"
 		    },
 		    {
 		    	"__name__": "GeneralizedPairState",
 		    	"name": "InsertX",
 		    	"startprob": 0.25,
 		    	"endprob": 1.0,
 		    	"durations": [[[1, 0], 1.0]],
 		    	"emission": {"__name__": "backgroundprob", "alphabet": "ACGT", 
 		    		         "tracks": 2, "track": 0,
 		    		         "distribution": {"__name__": "background-probability", "key": "value"}},
 		    	"onechar": "X"    	
 		    },
 		    {
 		    	"__name__": "GeneralizedPairState",
 		    	"name": "InsertY",
 		    	"startprob": 0.25,
 		    	"endprob": 1.0,
 		    	"durations": [[[0, 1], 1.0]],
 		    	"emission": {"__name__": "backgroundprob", "alphabet": "ACGT", 
 			                 "tracks": 2, "track": 1,
 		    		         "distribution": {"__name__": "background-probability", "key": "value"}},
 			    "onechar": "Y"    	
 		    }
 		]	
 	}
}
