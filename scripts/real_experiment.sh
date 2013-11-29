export PYTHONPATH=./

experiment_base="0009"

#mkdir -p data/experiments/repeat$experiment_base/alignments
#
#pypy \
#        scripts/annotateTRF.py \
#        data/alignments/hg-canFam-cftr-lastz-ensembl.fa \
#        data/experiments/repeat$experiment_base/hg-canFam-cftr-lastz-ensembl-trf.fa
#
#pypy \
#        scripts/split.py \
#        data/experiments/repeat$experiment_base/chr21.fa \
#        data/experiments/repeat$experiment_base/alignments/realign.{id}.fa \
#        data/experiments/repeat$experiment_base/alignments/keep.{id}.fa \
#        data/experiments/repeat$experiment_base/chr21.json \
#        275 50 50

#100838
#for X in 1-75000 75001-100839; do 
#qsub \
#        -N 'RealTrfLotTotal' \
#        -terse -cwd -t $X \
#        -o 'output' \
#        -e 'output' \
#        -v PYTHONPATH=./ \
#        -b y \
#        pypy-env/bin/pypy \
#                bin/Realign.py \
#                data/experiments/repeat$experiment_base/alignments/realign.{id}.fa \
#                data/experiments/repeat$experiment_base/alignments/realign.{id}.blockRepeatRealignerTrfLot.fa \
#                --model data/experiments/repeat0002/original_model.js \
#                --beam_width 30 \
#                --repeat_width 10 \
#                --sequence_regexp '^hg19.*' '^canFam.*' \
#                --tracks trf \
#                --resolve_indels True \
#                --algorithm repeat \
#                --merge_consensus True #\
##                --mathType LogNum 
#done
for X in 251-277 2112-2114; do #1-75000 75001-100839 80646-80705 88593-88594 89798-89802
qsub \
        -N 'RealTrfLotTotal' \
        -terse -cwd -t $X \
        -o 'output' \
        -e 'output' \
        -v PYTHONPATH=./ \
        -b y \
        pypy-env/bin/pypy \
                bin/Realign.py \
                data/experiments/repeat$experiment_base/alignments/realign.{id}.fa \
                data/experiments/repeat$experiment_base/alignments/realign.{id}.blockRepeatRealignerTrfLotHMM.fa \
                --model data/experiments/repeat0002/original_model.js \
                --beam_width 30 \
                --repeat_width 10 \
                --sequence_regexp '^hg19.*' '^canFam.*' \
                --tracks trf,hmm \
                --resolve_indels True \
                --algorithm repeat \
                --merge_consensus True #\
#                --mathType LogNum 
done

#pypy scripts/merge.py \
#    data/experiments/repeat$experiment_base/chr21.json \
###    data/experiments/repeat$experiment_base/chr21.realigned.80lines.fa \
#    blockRepeatRealignerTrfLot.fa
