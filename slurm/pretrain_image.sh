#!/bin/bash -l
#SBATCH --job-name=ctpY2
#SBATCH --time=0-48:0:0
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --mem=8G
#SBATCH --mail-type=end
#SBATCH --mail-user=cpaxton3@jhu.edu



export DATASET="ctp_dec"
export MODELDIR="$HOME/.costar/models_stack_Y1$1$3$2$4$5$6"

$HOME/costar_plan/costar_models/scripts/ctp_model_tool \
		--features multi \
		-e 100 \
		--model pretrain_image_encoder \
		--data_file $HOME/work/$DATASET.h5f \
		--lr 0.001 \
		--dropout_rate 0.5 \
		--decoder_dropout_rate 0.5 \
		--model_directory $MODELDIR/ \
		--optimizer adam \
		--use_noise true \
		--steps_per_epoch 500 \
		--noise_dim 32 \
		--hypothesis_dropout 1 \
		--upsampling conv_transpose \
		--skip_connections 0 \
		--batch_size 64


