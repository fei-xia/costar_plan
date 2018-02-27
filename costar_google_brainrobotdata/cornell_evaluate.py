'''
Evaluating a network on cornell grasping dataset.

In other words, this network tries to predict a grasp rectangle from an input image.

Apache License 2.0 https://www.apache.org/licenses/LICENSE-2.0

'''
import sys
import tensorflow as tf
import grasp_utilities
import cornell_grasp_train
from tensorflow.python.platform import flags
import cornell_grasp_train
import cornell_grasp_dataset_reader

# progress bars https://github.com/tqdm/tqdm
# import tqdm without enforcing it as a dependency
try:
    from tqdm import tqdm
except ImportError:

    def tqdm(*args, **kwargs):
        if args:
            return args[0]
        return kwargs.get('iterable', None)

FLAGS = flags.FLAGS


def main(_):

    # TODO(ahundt) remove the hardcoded folder or put it on a github release server
    kfold_params = '/home/ahundt/src/costar_ws/src/costar_plan/costar_google_brainrobotdata/logs_cornell/2018-02-26-22-57-58_200_epoch_real_run_-objectwise-kfold'
    cornell_grasp_train.model_predict_k_fold(kfold_params)
    # problem_type = 'grasp_regression'
    # feature_combo = 'image_preprocessed'
    # # Override some default flags for this configuration
    # # see other configuration in cornell_grasp_train.py choose_features_and_metrics()
    # FLAGS.problem_type = problem_type
    # FLAGS.feature_combo = feature_combo
    # FLAGS.crop_to = 'image_contains_grasp_box_center'
    # if FLAGS.load_hyperparams is None:
    #     FLAGS.load_hyperparams = '/home/ahundt/datasets/logs/hyperopt_logs_cornell/2018-02-23-09-35-21_-vgg_dense_model-dataset_cornell_grasping-grasp_success/2018-02-23-09-35-21_-vgg_dense_model-dataset_cornell_grasping-grasp_success_hyperparams.json'
    # FLAGS.split_dataset = 'objectwise'
    # FLAGS.epochs = 100

    # hyperparams = grasp_utilities.load_hyperparams_json(
    #     FLAGS.load_hyperparams, FLAGS.fine_tuning, FLAGS.learning_rate,
    #     feature_combo_name=feature_combo)


    # model_predict()
    # if 'k_fold' in FLAGS.pipeline_stage:
    #     cornell_grasp_train.train_k_fold(
    #         problem_name=problem_type,
    #         feature_combo_name=feature_combo,
    #         hyperparams=hyperparams,
    #         **hyperparams)
    # else:
    #     cornell_grasp_train.run_training(
    #         problem_name=problem_type,
    #         feature_combo_name=feature_combo,
    #         hyperparams=hyperparams,
    #         **hyperparams)

if __name__ == '__main__':
    # next FLAGS line might be needed in tf 1.4 but not tf 1.5
    # FLAGS._parse_flags()
    tf.app.run(main=main)
    print('grasp_train.py run complete, original command: ', sys.argv)
    sys.exit()