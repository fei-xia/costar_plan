#!/bin/bash -l

set -e
set -x
set -u

module load tensorflow/cuda-8.0/r1.3 

for lr in 0.01 0.001 0.0002 0.0001
do
  # just use the adam optimizer
  for opt in adam
  do
    for loss in mae # logcosh
    do
      # what do we do about skip connections?
      for skip in 0 # 1
      do
        # Noise: add extra ones with no noise at all
        for noise_dim in 0 # 1 8 32
        do
          hd=true
          for dr in 0.1 0.2 # 0. 0.3 0.4 0.5
          do
            sbatch stack_policy.sh $lr $dr $opt $noise_dim $loss
          done
        done
      done
    done
  done
done

