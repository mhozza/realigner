#!/bin/bash



for i in 1 5 10 20 40 80 160; do 
    let "a=$i * $i * 65 * 67";
    let "b=$i *65";
    let "c=$i*67";
    echo "$i: $b x $c == $a";
    time pypy hack/RepeatRealigner.py data/sequences/pokus$i.fa data/sequences/output$i.fa $1 > /dev/null;
done
