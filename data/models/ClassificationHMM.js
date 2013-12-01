{
  "contants": [
    {
      "__name__": "@trans?",
      "MM": 0.98,
      "MX": 0.01,
      "MY": 0.01,
      "XM": 0.9,
      "YM": 0.9,
      "XX": 0.09,
      "XY": 0.01,
      "YY": 0.09,
      "YX": 0.01
    }
  ],
  "model": {
    "__name__": "GeneralizedPairHMM",
    "transitions": [
      {
        "from": "Match",
        "to": "Match",
        "prob": {
          "__name__": "trans",
          "key": "MM"
        }
      },
      {
        "from": "Match",
        "to": "InsertX",
        "prob": {
          "__name__": "trans",
          "key": "MX"
        }
      },
      {
        "from": "Match",
        "to": "InsertY",
        "prob": {
          "__name__": "trans",
          "key": "MY"
        }
      },
      {
        "from": "InsertX",
        "to": "Match",
        "prob": {
          "__name__": "trans",
          "key": "XM"
        }
      },
      {
        "from": "InsertX",
        "to": "InsertX",
        "prob": {
          "__name__": "trans",
          "key": "XX"
        }
      },
      {
        "from": "InsertX",
        "to": "InsertY",
        "prob": {
          "__name__": "trans",
          "key": "XY"
        }
      },
      {
        "from": "InsertY",
        "to": "Match",
        "prob": {
          "__name__": "trans",
          "key": "YM"
        }
      },
      {
        "from": "InsertY",
        "to": "InsertX",
        "prob": {
          "__name__": "trans",
          "key": "YX"
        }
      },
      {
        "from": "InsertY",
        "to": "InsertY",
        "prob": {
          "__name__": "trans",
          "key": "YY"
        }
      }
    ],
    "states": [
      {
        "__name__": "ClassifierState",
        "name": "Match",
        "startprob": 0.33,
        "endprob": 1.0,
        "durations": [
          [
            [
              1,
              1
            ],
            1.0
          ]
        ],
        "emission": {},
        "onechar": "M"
      },
      {
        "__name__": "SimpleState",
        "name": "InsertX",
        "startprob": 0.33,
        "endprob": 1.0,
        "durations": [
          [
            [
              1,
              0
            ],
            1.0
          ]
        ],
        "emission": {},
        "onechar": "X"
      },
      {
        "__name__": "SimpleState",
        "name": "InsertY",
        "startprob": 0.33,
        "endprob": 1.0,
        "durations": [
          [
            [
              0,
              1
            ],
            1.0
          ]
        ],
        "emission": {},
        "onechar": "Y"
      }
    ]
  }
}
