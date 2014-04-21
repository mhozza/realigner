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
        "emission": [
          [
            [
              "A",
              "A"
            ],
            0.16829558998808106
          ],
          [
            [
              "A",
              "T"
            ],
            0.026758045292014303
          ],
          [
            [
              "T",
              "T"
            ],
            0.17806912991656734
          ],
          [
            [
              "T",
              "A"
            ],
            0.026758045292014303
          ],
          [
            [
              "G",
              "G"
            ],
            0.17234803337306318
          ],
          [
            [
              "C",
              "T"
            ],
            0.027234803337306317
          ],
          [
            [
              "T",
              "C"
            ],
            0.027234803337306317
          ],
          [
            [
              "G",
              "A"
            ],
            0.02437425506555423
          ],
          [
            [
              "G",
              "T"
            ],
            0.027234803337306317
          ],
          [
            [
              "A",
              "C"
            ],
            0.02497020262216925
          ],
          [
            [
              "A",
              "G"
            ],
            0.02437425506555423
          ],
          [
            [
              "G",
              "C"
            ],
            0.024493444576877233
          ],
          [
            [
              "C",
              "C"
            ],
            0.17115613825983314
          ],
          [
            [
              "T",
              "G"
            ],
            0.027234803337306317
          ],
          [
            [
              "C",
              "G"
            ],
            0.024493444576877233
          ],
          [
            [
              "C",
              "A"
            ],
            0.02497020262216925
          ]
        ],
        "onechar": "M",
        "__name__": "SimpleMatchState"
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
        "emission": [
          [
            "A",
            0.2526041666666667
          ],
          [
            "C",
            0.23046875
          ],
          [
            "T",
            0.25390625
          ],
          [
            "G",
            0.2630208333333333
          ]
        ],
        "onechar": "X",
        "__name__": "SimpleIndelState"
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
        "emission": [
          [
            "A",
            0.2526041666666667
          ],
          [
            "C",
            0.23046875
          ],
          [
            "T",
            0.25390625
          ],
          [
            "G",
            0.2630208333333333
          ]
        ],
        "onechar": "Y",
        "__name__": "SimpleIndelState"
      }
    ],
    "__name__": "GeneralizedPairHMM",
    "transitions": [
      {
        "to": "Match",
        "from": "Match",
        "prob": 0.980808201215878
      },
      {
        "to": "InsertX",
        "from": "Match",
        "prob": 0.008821075217546787
      },
      {
        "to": "InsertY",
        "from": "Match",
        "prob": 0.010370723566575276
      },
      {
        "to": "Match",
        "from": "InsertX",
        "prob": 0.1111111111111111
      },
      {
        "to": "InsertX",
        "from": "InsertX",
        "prob": 0.8833333333333333
      },
      {
        "to": "InsertY",
        "from": "InsertX",
        "prob": 0.005555555555555556
      },
      {
        "to": "Match",
        "from": "InsertY",
        "prob": 0.09926470588235294
      },
      {
        "to": "InsertX",
        "from": "InsertY",
        "prob": 0.012254901960784314
      },
      {
        "to": "InsertY",
        "from": "InsertY",
        "prob": 0.8884803921568627
      }
    ]
  }
}
