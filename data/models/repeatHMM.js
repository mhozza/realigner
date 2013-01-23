// TODO: Clean names
{
    "contants": [
 	    {
 	        "__name__": "@trans?",   	 
	        "MM": 0.91,
	        "MI": 0.03,
	        "MR": 0.03,
	        "IM": 0.91,
	        "II": 0.03,
	        "IR": 0.03,
	        "RM": 0.91,
	        "RI": 0.03,
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
        	"value": [("A", 0.25), ("C", 0.25), ("G", 0.25), ("T", 0.25)]
        },
        {
        	"__name__": "@repeat-transitions?",
        	"value": {
        		"MM": 0.92,
	        	"MI": 0.04,
	        	"MD": 0.04,
	            "IM": 0.1,
	            "II": 0.85,
	            "ID": 0.05,
	            "DM": 0.1,
	            "DI": 0.1,
	            "DD": 0.8,
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
 		    		"timeX": {"__name__": "times", "key": "jukes-cantor-pair-state-time-X"},
 		    		"timeY": {"__name__": "times", "key": "jukes-cantor-pair-state-time-Y"},
 		        	"backgroundprob": {"__name__": "background-probability", "key": "value"}
 		    	},
 		    	"onechar": "M"
 		    },
 		    {
 		    	"__name__": "GeneralizedPairState",
 		    	"name": "InsertX",
 		    	"startprob": 0.25,
 		    	"endprob": 1.0,
 		    	"durations": [[[1, 0], 1.0]],
 		    	"emission": {"__name__": "backgroundprob", "alphabet": "ACGT", 
 		    		         "tracks": 2, "track": 0},
 		    	"onechar": "X"    	
 		    },
 		    {
 		    	"__name__": "GeneralizedPairState",
 		    	"name": "InsertY",
 		    	"startprob": 0.25,
 		    	"endprob": 1.0,
 		    	"durations": [[[0, 1], 1.0]],
 		    	"emission": {"__name__": "backgroundprob", "alphabet": "ACGT", 
 			                 "tracks": 2, "track": 1},
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
 		    	"backgroundprobability": {"__name__": "background-probability", "key": "value"},
 		    	"transitionmatrix": {"__name__": "repeat-transitions", "key": "value"},
 		    	"consensusdistribution": {"__name__": "#file(consensus.js)"},
 		    	"repeatlengthdistribution": {"__name__": "#file(repeatlength.js)"}
 		    }
 		]	
 	}
}