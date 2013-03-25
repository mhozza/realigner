{
    "contants": [
 	    {
 	        "__name__": "@trans?",   	 
	        "MM": 0.91,
	        "MX": 0.03,
	        "MY": 0.03,
	        "MR": 0.03,
	        "XM": 0.91,
	        "YM": 0.91,
	        "XX": 0.03,
	        "XY": 0.03,
	        "YY": 0.03,
	        "YX": 0.03,
	        "XR": 0.03,
	        "YR": 0.03,
	        "RM": 0.91,
	        "RX": 0.03,
	        "RY": 0.03,
	        "RR": 0.03
        },
        {
        	"__name__": "@times?",
        	"jukes-cantor-pair-state-time-X": 0.00005,
        	"jukes-cantor-pair-state-time-Y": 0.00005,
        	"jukes-cantor-repeat-state-time": 0.00000005
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
        },
        {
        	"__name__": "@repeat-transitions?",
        	"value": {
        		"MM": 0.99,
	        	"MI": 0.005,
	        	"MD": 0.005,
	            "IM": 0.99,
	            "II": 0.005,
	            "ID": 0.005,
	            "DM": 0.99,
	            "DI": 0.005,
	            "DD": 0.005,
	            "_M": 0.8,
	            "_I": 0.1,
	            "_D": 0.1
        	}
        }
    ],
 	"model": {
 		"__name__": "GeneralizedPairHMM",
 		"transitions": [
 		    {"from": "Match", "to": "Match", "prob": {"__name__": "trans", "key": "MM"}},
 		    {"from": "Match", "to": "InsertX", "prob": {"__name__": "trans", "key": "MX"}},
 		    {"from": "Match", "to": "InsertY", "prob": {"__name__": "trans", "key": "MY"}},
 		    {"from": "Match", "to": "Repeat", "prob": {"__name__": "trans", "key": "MR"}},
 		    {"from": "InsertX", "to": "Match", "prob": {"__name__": "trans", "key": "XM"}},
 		    {"from": "InsertX", "to": "InsertX", "prob": {"__name__": "trans", "key": "XX"}},
 		    {"from": "InsertX", "to": "InsertY", "prob": {"__name__": "trans", "key": "XY"}},
 		    {"from": "InsertX", "to": "Repeat", "prob": {"__name__": "trans", "key": "XR"}},
 		    {"from": "InsertY", "to": "Match", "prob": {"__name__": "trans", "key": "YM"}},
 		    {"from": "InsertY", "to": "InsertX", "prob": {"__name__": "trans", "key": "YX"}},
 		    {"from": "InsertY", "to": "InsertY", "prob": {"__name__": "trans", "key": "YY"}},
 		    {"from": "InsertY", "to": "Repeat", "prob": {"__name__": "trans", "key": "YR"}},
 		    {"from": "Repeat", "to": "Match", "prob": {"__name__": "trans", "key": "RM"}},
 		    {"from": "Repeat", "to": "InsertX", "prob": {"__name__": "trans", "key": "RX"}},
 		    {"from": "Repeat", "to": "InsertY", "prob": {"__name__": "trans", "key": "RY"}},
 		    {"from": "Repeat", "to": "Repeat", "prob": {"__name__": "trans", "key": "RR"}}
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
 		    },
 		    {
 		    	"__name__": "PairRepeatState", 
 		    	"name": "Repeat",
 		    	"startprob": 0.25,
 		    	"endprob": 1.0,
 		    	"durations": [],
 		    	"emission": [],
 		    	"onechar": "R",
 		    	"time": {"__name__": "times", "key": "jukes-cantor-repeat-state-time"},
 		    	"backgroundprob": {"__name__": "background-probability", "key": "value"},
 		    	"transitionmatrix": {"__name__": "repeat-transitions", "key": "value"},
 		    	"consensusdistribution": {"__name__": "#file(consensus.js)"},
 		    	"repeatlengthdistribution": {
 		    		"__name__": "RepeatLengthDistribution",
 		    		"data": {"__name__": "#file(repeatlength.js)"},
 		    		"fractionssize": 10,
 		    		"start": 2
 		    	}
 		    }
 		]	
 	}
}
