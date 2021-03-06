
# Experiments and Training Notes for Task Learning

This document is for the full set of task learning experiments, and contains notes on how to run them and reproduce them.

For most of these examples, we will use the [simulation dataset](https://github.com/cpaxton/costar_plan/releases/download/v0.6.0/simdata.tar.gz) that was included with the v0.6.0 release of CoSTAR-Plan. The primary model associated with this is the `conditional_image` model, which trains on generating a set of predictive images from simulated data.

Commands for reproducing the submitted paper results were current as of 2018-03-30.

## Learning Commands

This contains some examples of commands you can run on different data sets.

### Stacking Task

The stacking task uses the [simulation dataset](https://github.com/cpaxton/costar_plan/releases/download/v0.6.0/simdata.tar.gz). You can run the simulation with the `costar_bullet` tool, and PyBullet v1.2.2.

## Discriminator and Goal Discriminator

This command generates the goal discriminator, which provides an additional loss to the real final model. In essence, it tries to classify which action is being performed at a given time step. This model is trained on the actual input data, not on any hallucinated outputs.

```
export CUDA_VISIBLE_DEVICES="0" && rosrun costar_models ctp_model_tool --model goal_discriminator --data_file ~/datasets/costar_plan/data.h5f --lr 0.001 --dropout_rate 0.1 --retrain
```

Dataset files will be in a certain format like hdf5 in a directory. Please note that the `data_file` path doesn't have to be the name of the actual file, the folder and extension will be used to extract all the relevant files from the folder.

#### Pretrain Encoders

You can pretrain autoencoders with:

```
rosrun costar_models ctp_model_tool --model pretrain_image_encoder --data_file data.h5f --lr 0.001 --dropout_rate 0.1
```

I recommend using the `feh` tool to visualize results:
```
sudo apt-get install feh
```

Now you can start visualizing images as the model trains:
```
feh ~/.costar/models/debug
```

Remember at any time you can change the model output path with the `--model_directory` flag.

#### Conditional Images

The `conditional_image` model is the main predictive model, which trains on predicting the results of the next two high level actions.

Example command from 2018-03-30:
```
export CUDA_VISIBLE_DEVICES="0" && rosrun costar_models ctp_model_tool --model conditional_image --data_file ~/datasets/costar_plan/data.h5f --lr 0.001 --dropout_rate 0.1 --retrain
```

Example command after update to glob syntax, about 2018-04:
```
export CUDA_VISIBLE_DEVICES="0" && rosrun costar_models ctp_model_tool --model conditional_image --dropout_rate 0.1 --ssm 0 --data_file small_robot2.h5f --lr 0.001 --features costar -e 150 --model_directory $HOME/.costar/models --skip_connections 1 --use_ssm 0 --batch_size 64 --no_disc --steps_per_epoch 1600 --retrain --data_file "~/datasets/costar_task_planning_stacking_dataset_v0.2/small/*.h5f"
```

Notes on flags:
  - The default optimizer setting is `--optimizer adam`.
  - `--lr` sets the learning rate.
  - `--dropout_rate 0.1` sets 10% dropout, which is what we used in the paper.
  - `--retrain` tells it to train the encoder and decoder end-to-end. This is a new addition, not in the paper.

This will train the main model which hallucinates possible futures and save the output into `~/.costar/models`, where you can view image files of the progress.

```
# Start training
rosrun costar_models ctp_model_tool --model conditional_image --data_file data.h5f --lr 0.001 --dropout_rate 0.1

# Resume training
rosrun costar_models ctp_model_tool --model conditional_image --data_file data.h5f --lr 0.001 --dropout_rate 0.1 --load_model

# Retrain encoder and decoder end-to-end
rosrun costar_models ctp_model_tool --model conditional_image --data_file data.h5f --lr 0.001 --dropout_rate 0.1 --retrain
```

#### Conditional Image GAN

This version runs the conditional image GAN:

```
rosrun costar_models ctp_model_tool --model conditional_image_gan --data_file data.h5f --lr 0.0002 --dropout_rate 0.2 
```

To train it end-to-end add the `--retrain` flag:
```
# Retrain encoders and decoders with "--retrain"
rosrun costar_models ctp_model_tool --model conditional_image_gan --data_file data.h5f --lr 0.0002 --dropout_rate 0.2 --retrain

# Alternately, specify the model set we want to use with "--features multi":
# Adding the "--steps_per_epoch" flag can get you faster feedback when things
# aren't working
rosrun costar_models ctp_model_tool --model conditional_image_gan --features multi --data_file data.h5f --lr 0.0002 --dropout_rate 0.2 --steps_per_epoch 500
```

[Example script.](../commands/multi_conditional_image_gan.sh) Different values for dropout rate and for learning rate might be useful.

#### Training Policies

We also learn "actor" networks that operate on the current world state. These are trained with the `ff_regression` and `hierachical` models.

```
# Use the --success_only flag to make sure we don't learn bad things
rosrun costar_models ctp_model_tool --model hierarchical --data_file data.h5f --lr 0.001 --dropout_rate 0.2 --success_only
```

The advantage here is that they can use a little bit more information than the previous versions should it prove necessary. They are also trained end-to-end, since there is no need for them to produce high quality images.

### Husky Experiments

First, you need a data set. Here we assume this was placed in `husky_data`, and consists of numpy blobs.

```
# Set "--features husky" to use husky versions of models
rosrun costar_models ctp_model_tool --model pretrain_image_encoder --features husky --data_file husky_data.npz --lr 0.001 --dropout_rate 0.2
```

Alternately, you can train the GAN version:

```
# Start gan with the pre-collected husky dataset, containing both successes and
# failures.
# Learning rate set to 0.0002 as per "Image to Image Translation..." paper.
rosrun costar_models ctp_model_tool --model pretrain_image_gan --features husky --data_file husky_data.npz --lr 0.0002 --dropout_rate 0.2
```
[GAN example script](../commands/husky_pretrain_image_gan.sh)

### Jigsaws Experiments

```
# Run the jigsaws data to learn encoder
rosrun costar_models ctp_model_tool --model pretrain_image --data_file suturing_data.h5f --lr 0.001 --dropout_rate 0.2 --features jigsaws --batch_size 32

# Run the jigsaws data to learn encoder via GAN
rosrun costar_models ctp_model_tool --model pretrain_image_gan --data_file suturing_data.h5f --lr 0.001 --dropout_rate 0.2 --features jigsaws --batch_size 32
```

#### Wasserstein GAN

We also implemented Wasserstein GAN training.

```
# Run with wasserstein GAN loss
rosrun costar_models ctp_model_tool --model pretrain_image_gan \
  --features jigsaws --batch_size 64 --data_file suturing_data2.h5f \
  --lr 0.00005 --optimizer rmsprop --steps_per_epoch 100 \
  --dropout_rate 0.1 --load_model --preload  --wasserstein
```

Some options here:
  - `--preload` will try to store the whole data set in memory for faster procesing
  - `--wasserstein` will tell the GAN to try something different (wasserstein loss)

Here's a version for the "multi" dataset:

```
./costar_models/scripts/ctp_model_tool --model conditional_image_gan \
  --dropout_rate 0.1 --data_file data.h5f --lr 0.00005 --features multi \
  --preload --batch_size 64 --gpu_fraction 1 --wasserstein \
  --optimizer rmsprop --steps_per_epoch 100 
```

## Training On MARCC

MARCC is our cluster for machine learning, equipped with a large set of Tesla K80 GPUs. We assume that when training on a cluster like MARCC, you will not want a full ROS workspace, so instead we assume you will install to some path $COSTAR_PLAN and just run scripts.

To run on MARCC, the easiest set up is always:
```
export COSTAR_PLAN=$HOME/costar_plan
$COSTAR_PLAN/slurm/start_ctp_stacks.sh
```

This will run the `$COSTAR_PLAN/slurm/ctp.sh$ script with a few different arguments to start SLURM jobs.


## Validation

### Hidden State

You can visualize the hidden state learned with models like `pretrain_image_encoder`, `pretrain_image_gan`, and `pretrain_sampler` with the `ctp_hidden.py` tool:

```
rosrun costar_models ctp_hidden.py --cpu --model conditional_image --data_file test2.h5f
```

The learned representations come in 8 x 8 x 8 = 512 dimensions by default. This tool is meant to visualize representations that are eight channels or so. This includes some spatial information; take a look at the examples below. You'll see information seems to have some spatial correlation to the original image.

![Encoding blocks on the right](hidden1.png)

This changes dramatically when we compare to a representation where all the blocks are now on the left:

![Encoding blocks on the left](hidden2.png)

### Transformation

```
rosrun costar_models ctp_transform.py --cpu --model conditional_image --data_file test2.h5f
```

