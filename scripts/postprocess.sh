#!/bin/bash

for basenam in `ls data/experiments/repeat0008/sampled_test_short_aln/aln_0.sff_*_cor.fa | sed -e 's/.*0.//;s/.fa$//' |grep -v postprocessed | grep mic_ma` ; do
        echo $basenam `date`
        time for i in `seq -1 200`; do 
            let "a = $i + 1"
            perl brona/realign_repeats.pl \
                brona/real-data2/simple0008.hmm \
                data/experiments/repeat0008/sampled_test_short_aln/aln_$a.$basenam.fa \
                /tmp/mic/lol \
                > data/experiments/repeat0008/sampled_test_short_aln/aln_$a.${basenam}_postprocessed.fa 
        done
done
