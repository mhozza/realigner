{"contants": [null], "model": {"states": [{"name": "Match", "durations": [[[1, 1], 1.0]], "startprob": 0.33, "endprob": 1.0, "emission": [[["C", "G"], 0.07065461384456713], [["A", "T"], 0.07060607899047504], [["T", "T"], 0.03831826730570891], [["T", "A"], 0.07084875326093551], [["G", "G"], 0.0391312261117515], [["C", "T"], 0.07087302068798156], [["T", "C"], 0.06993872474670873], [["G", "A"], 0.0706424801310441], [["G", "T"], 0.07070314869865922], [["C", "A"], 0.07152824121822483], [["A", "G"], 0.06981738761147849], [["C", "C"], 0.038718679851968696], [["T", "G"], 0.07104289267730389], [["A", "A"], 0.03792998847297215], [["G", "C"], 0.0685918825456531], [["A", "C"], 0.07065461384456713]], "onechar": "M", "__name__": "SimpleMatchState"}, {"name": "InsertX", "durations": [[[1, 0], 1.0]], "startprob": 0.33, "endprob": 1.0, "emission": [["A", 0.23593972135342622], ["C", 0.23611032129655957], ["T", 0.23611032129655957], ["G", 0.2365652544782485]], "onechar": "X", "__name__": "SimpleIndelState"}, {"name": "InsertY", "durations": [[[0, 1], 1.0]], "startprob": 0.33, "endprob": 1.0, "emission": [["A", 0.23593972135342622], ["C", 0.23611032129655957], ["T", 0.23611032129655957], ["G", 0.2365652544782485]], "onechar": "Y", "__name__": "SimpleIndelState"}], "__name__": "GeneralizedPairHMM", "transitions": [{"to": "Match", "from": "Match", "prob": 0.9792028150215374}, {"to": "InsertX", "from": "Match", "prob": 0.010495662197415519}, {"to": "InsertY", "from": "Match", "prob": 0.010301522781047139}, {"to": "Match", "from": "InsertX", "prob": 0.10477001703577513}, {"to": "InsertX", "from": "InsertX", "prob": 0.8886590411292286}, {"to": "InsertY", "from": "InsertX", "prob": 0.006570941834996349}, {"to": "Match", "from": "InsertY", "prob": 0.10150107219442459}, {"to": "InsertX", "from": "InsertY", "prob": 0.005956635692161067}, {"to": "InsertY", "from": "InsertY", "prob": 0.8925422921134143}]}}