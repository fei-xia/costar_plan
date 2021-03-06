#!/bin/bash -l
#SBATCH --job-name=jigsaws
#SBATCH --time=0-48:0:0
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --mem=8G
#SBATCH --mail-type=end
#SBATCH --mail-user=cpaxton3@uuuuuu


echo "Running $@ on $SLURMD_NODENAME ..."
echo $1 $2 $3 $4 $5 $6 $7 $8 $9
echo "use disc = $use_disc"

export DATASET="suturing_data2"
export train_discriminator2=false
export train_image_encoder=false
export learning_rate=$1
export dropout=$2
export optimizer=$3
export noise_dim=$4
export loss=$5
export retrain=$6
export use_disc=$7
export use_skips=$8
export use_ssm=$9
#export MODELDIR="$HOME/.costar/suturing_$learning_rate$optimizer$dropout$noise_dim$loss"
export MODELROOT="$HOME/.costar"
export SUBDIR="suturing_$learning_rate$optimizer$dropout$noise_dim${loss}_skip${use_skips}_ssm${use_ssm}"
export USE_BN=1

retrain_cmd=""

use_disc_cmd=""
if ! $use_disc ; then
  use_disc_cmd="--no_disc"
  SUBDIR=${SUBDIR}_nodisc
fi

export MODELDIR="$MODELROOT/$SUBDIR"
mkdir $MODELDIR
touch $MODELDIR/$SLURM_JOB_ID

export learning_rate_disc=0.01
export learning_rate_enc=0.01

echo "Options are: $retrain_cmd $use_disc_cmd $1 $2 $3 $4 $5"
echo "Directory is $MODELDIR"
echo "Slurm job ID = $SLURM_JOB_ID"

if $train_discriminator2
then
  echo "Training discriminator 2"
  $HOME/costar_plan/costar_models/scripts/ctp_model_tool \
    -e 100 \
    --model goal_discriminator \
    --data_file $HOME/work/$DATASET.h5f \
    --lr $learning_rate \
    --features jigsaws \
    --preload \
    --dropout_rate $dropout \
    --model_directory $MODELDIR/ \
    --optimizer $optimizer \
    --steps_per_epoch 150 \
    --noise_dim $noise_dim \
    --use_batchnorm $USE_BN \
    --loss $loss \
    --batch_size 64
fi

$HOME/costar_plan/costar_models/scripts/ctp_model_tool \
  --features multi \
  -e 200 \
  --model conditional_image \
  --data_file $HOME/work/$DATASET.h5f \
  --lr $learning_rate \
  --dropout_rate $dropout \
  --model_directory $MODELDIR/ \
  --features jigsaws \
  --optimizer $optimizer \
  --steps_per_epoch 300 \
  --preload \
  --loss $loss \
  --use_batchnorm $USE_BN \
  --skip_connections $use_skips \
  --use_ssm $use_ssm \
  --batch_size 64 --retrain $use_disc_cmd

