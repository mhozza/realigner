{"contants": [null], "model": {"states": [{"name": "Match", "durations": [[[1, 1], 1.0]], "startprob": 0.33, "endprob": 1.0, "emission": [[["C", "G"], 0.03210191082802548], [["A", "T"], 0.032356687898089175], [["T", "T"], 0.15304822565969062], [["T", "A"], 0.032356687898089175], [["G", "G"], 0.15399454049135577], [["C", "T"], 0.03130118289353958], [["T", "C"], 0.03130118289353958], [["G", "A"], 0.032332423415225964], [["G", "T"], 0.03140430694570822], [["A", "G"], 0.032332423415225964], [["A", "A"], 0.15451622687291477], [["C", "C"], 0.15551107067030634], [["T", "G"], 0.03140430694570822], [["G", "C"], 0.03210191082802548], [["A", "C"], 0.03196845617227783], [["C", "A"], 0.03196845617227783]], "onechar": "M", "__name__": "SimpleMatchState"}, {"name": "InsertX", "durations": [[[1, 0], 1.0]], "startprob": 0.33, "endprob": 1.0, "emission": [["A", 0.25043198474646966], ["C", 0.2445927426562593], ["T", 0.24268605136149676], ["G", 0.2622892212357743]], "onechar": "X", "__name__": "SimpleIndelState"}, {"name": "InsertY", "durations": [[[0, 1], 1.0]], "startprob": 0.33, "endprob": 1.0, "emission": [["A", 0.25043198474646966], ["C", 0.2445927426562593], ["T", 0.24268605136149676], ["G", 0.2622892212357743]], "onechar": "Y", "__name__": "SimpleIndelState"}], "__name__": "GeneralizedPairHMM", "transitions": [{"to": "Match", "from": "Match", "prob": 0.9804911190915268}, {"to": "InsertX", "from": "Match", "prob": 0.010191206444724838}, {"to": "InsertY", "from": "Match", "prob": 0.009317674463748423}, {"to": "Match", "from": "InsertX", "prob": 0.09730729226857737}, {"to": "InsertX", "from": "InsertX", "prob": 0.8991101352132208}, {"to": "InsertY", "from": "InsertX", "prob": 0.0035825725182017797}, {"to": "Match", "from": "InsertY", "prob": 0.0942189421894219}, {"to": "InsertX", "from": "InsertY", "prob": 0.004059040590405904}, {"to": "InsertY", "from": "InsertY", "prob": 0.9017220172201722}]}}