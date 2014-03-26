{
  "contants": [
    null
  ],
  "model": {
    "states": [
      {
        "name": "Match",
        "durations": [
          [
            [
              1,
              1
            ],
            1.0
          ]
        ],
        "startprob": 0.33,
        "endprob": 1.0,
        "emission": [],
        "onechar": "M",
        "__name__": "ClassifierState"
      },
      {
        "name": "InsertX",
        "durations": [
          [
            [
              1,
              0
            ],
            1.0
          ]
        ],
        "startprob": 0.33,
        "endprob": 1.0,
        "emission": [],
        "onechar": "X",
        "__name__": "ClassifierIndelState"
      },
      {
        "name": "InsertY",
        "durations": [
          [
            [
              0,
              1
            ],
            1.0
          ]
        ],
        "startprob": 0.33,
        "endprob": 1.0,
        "emission": [],
        "onechar": "Y",
        "__name__": "ClassifierIndelState"
      }
    ],
    "__name__": "GeneralizedPairHMM",
    "transitions": [
      {
        "to": "Match",
        "from": "Match",
        "prob": 0.9804911190915268
      },
      {
        "to": "InsertX",
        "from": "Match",
        "prob": 0.010191206444724838
      },
      {
        "to": "InsertY",
        "from": "Match",
        "prob": 0.009317674463748423
      },
      {
        "to": "Match",
        "from": "InsertX",
        "prob": 0.09730729226857737
      },
      {
        "to": "InsertX",
        "from": "InsertX",
        "prob": 0.8991101352132208
      },
      {
        "to": "InsertY",
        "from": "InsertX",
        "prob": 0.0035825725182017797
      },
      {
        "to": "Match",
        "from": "InsertY",
        "prob": 0.0942189421894219
      },
      {
        "to": "InsertX",
        "from": "InsertY",
        "prob": 0.004059040590405904
      },
      {
        "to": "InsertY",
        "from": "InsertY",
        "prob": 0.9017220172201722
      }
    ]
  }
}
