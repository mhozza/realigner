from adapters.TRFDriver import TRFDriver, trf_paths
import os
import json
import sys

if len(sys.argv) < 3:
    print "Nedostatok argumentov."
    exit(1)
alignment_filename = sys.argv[1]
output_file = sys.argv[2]

trf = None
for trf_executable in trf_paths:
    if os.path.exists(trf_executable):
        trf = TRFDriver(trf_executable, mathType=float)
if trf:
    repeats = trf.run(alignment_filename)
    for k, v in repeats.iteritems():
        repeats[k] = [(r.start, r.end, r.repetitions, r.consensus, r.sequence) for r in v]
    with open(output_file, 'w') as f:
        json.dump(repeats, f, indent=4)

