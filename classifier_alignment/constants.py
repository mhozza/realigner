__author__ = 'michal'

bases = {
    'A': 0,
    'C': 1,
    'G': 2,
    'T': 3,
    'N': 4,
    '-': -1,  # gap value
}

bases_reverse = {v: k for k, v in bases.iteritems()}

window_size = 5
annotations_enabled = True
boost = 5
