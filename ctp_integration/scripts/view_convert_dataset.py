'''
View and Convert dataset lets you look at the video data in a costar stacking dataset.

show a video from an h5f file:

    python view_convert_dataset --path <path/to/data/folder/or/file> --preview True

Convert video from an h5f file into a gif:

python plot_graph --path 'data/' 
    python view_convert_dataset --path <path/to/data/folder/or/file> --preview --convert gif
'''
import argparse
import os
import numpy as np
import h5py 
import matplotlib.pyplot as plt
# https://github.com/tanyaschlusser/array2gif
# from array2gif import write_gif

# progress bars https://github.com/tqdm/tqdm
# import tqdm without enforcing it as a dependency
try:
    from tqdm import tqdm
except ImportError:

    def tqdm(*args, **kwargs):
        if args:
            return args[0]
        return kwargs.get('iterable', None)

from costar_models.datasets.image import JpegToNumpy
from costar_models.datasets.image import ConvertImageListToNumpy
import pygame
import io
from PIL import Image
import moviepy
import moviepy.editor as mpye
# import skimage




def npy_to_video(npy, filename, fps=10, preview=True, convert='gif'):
    """Convert a numpy array into a gif file at the location specified by filename.
        
        # Arguments

        convert: Default empty string is no conversion, options are gif and mp4.
        preview: pop open a preview window to view the video data.
    """
    # Useful moviepy instructions https://github.com/Zulko/moviepy/issues/159
    # TODO(ahundt) currently importing moviepy prevents python from exiting. Once this is resolved remove the import below.
    import moviepy.editor as mpy
    clip = mpy.ImageSequenceClip(list(npy), fps)
    if preview:
        # https://stackoverflow.com/a/41771413
        clip.preview()
    if convert == 'gif':
        clip.write_gif(filename)
    elif convert:
        clip.write_videofile(filename)

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, default=os.path.join(os.path.expanduser("~"), '.costar', 'data'),
                        help='path to dataset h5f file or folder containing many files')
    parser.add_argument("--convert", type=str, default='',
                        help='format to convert images to. Default empty string is no conversion, options are gif and mp4.')
    parser.add_argument("--ignore_failure", type=bool, default=False, help='skip grasp failure cases')
    parser.add_argument("--ignore_success", type=bool, default=False, help='skip grasp success cases')
    parser.add_argument("--ignore_error", type=bool, default=False, help='skip grasp attempts that are both failures and contain errors')
    parser.add_argument("--preview", type=bool, default=False, help='pop open a preview window to view the video data')
    parser.add_argument("--depth", type=bool, default=True, help='process depth data')
    parser.add_argument("--rgb", type=bool, default=True, help='process rgb data')
    parser.add_argument("--fps", type=int, default=10, help='framerate to process images in frames per second')
    parser.add_argument("--matplotlib", type=bool, default=False, 
                        help='preview data with matplotlib, slower but you can do pixel lookups')
    return vars(parser.parse_args())

def draw_matplotlib(depth_images, fps):
    for image in tqdm(depth_images):
        plt.imshow(image)
        plt.pause(1.0 / fps)
        plt.draw()

def main(args,root="root"):

    if '.h5f' in args['path']:
        filenames = [args['path']]
    else:
        filenames = os.listdir(args['path'])

    # Read data
    progress_bar = tqdm(filenames)
    for filename in progress_bar: 
        print('ignore error: ' + str(args['ignore_error']))
        if filename.startswith('.') or '.h5' not in filename:
            continue
        if args['ignore_error'] and 'error' in filename:
            progress_bar.write('Skipping example containing errors: ' + filename)
            continue
        if args['ignore_failure'] and 'failure' in filename:
            progress_bar.write('Skipping example containing failure: ' + filename)
            continue
        if args['ignore_success'] and 'success' in filename:
            progress_bar.write('Skipping example containing success: ' + filename)
            continue

        if args['path'] not in filename:
            # prepend the path if it isn't already present
            example_filename = os.path.join(args['path'], filename)
        else:
            example_filename = filename
        progress_bar.set_description("Processing %s" % example_filename)

        data = h5py.File(example_filename,'r')

        fps=args['fps']

        if args['depth']:
            depth_images = list(data['depth_image'])
            depth_images = ConvertImageListToNumpy(np.squeeze(depth_images), format='list')
            if args['matplotlib']:
                draw_matplotlib(depth_images, fps)
            depth_clip = mpye.ImageSequenceClip(depth_images, fps=fps)
            clip = depth_clip
        if args['rgb']:
            rgb_images = list(data['image'])
            rgb_images = ConvertImageListToNumpy(np.squeeze(rgb_images), format='list')
            if args['matplotlib']:
                draw_matplotlib(rgb_images, fps)
            rgb_clip = mpye.ImageSequenceClip(rgb_images, fps=fps)
            clip = rgb_clip
        
        if args['rgb'] and args['depth']:
            clip = mpye.clips_array([[rgb_clip, depth_clip]])
        
        if args['preview']:
            clip.preview()

        save_filename = example_filename.replace('.h5f','.' + args['convert'])
        if 'gif' in args['convert']:
            clip.write_gif(save_filename)
        elif args['convert']:
            clip.write_videofile(filename)

if __name__ == "__main__":
    args = _parse_args()
    main(args)