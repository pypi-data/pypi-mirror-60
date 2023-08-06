import logging
import argparse

import matplotlib.pyplot as plt
import numpy as np

import torch
from ctapipe.instrument import CameraGeometry
from ctapipe.visualization import CameraDisplay
from astropy import units as u
from PIL import Image
from torchvision import transforms
import torchvision.utils as t_utils
from tensorboardX import SummaryWriter
import indexedconv.utils as cvutils


# TODO find a cleverer method to infer kernel shape
def get_idx_matrix_from_kernel(kernel_length):
    if kernel_length == 4:
        kernel = np.ones((2, 2), dtype=bool)
    elif kernel_length == 19:
        kernel = np.ones((5, 5), dtype=bool)
        kernel[0, 3:5] = False
        kernel[1, 4] = False
        kernel[3:5, 0] = False
        kernel[4, 1] = False
    elif kernel_length == 9:
        kernel = np.ones((3, 3), dtype=bool)
    elif kernel_length == 7:
        kernel = np.ones((3, 3), dtype=bool)
        kernel[0, 2] = False
        kernel[2, 0] = False
    idx = 0
    index_matrix = np.ones(kernel.shape) * -1
    for i in range(kernel.shape[0]):
        for j in range(kernel.shape[1]):
            if kernel[i, j]:
                index_matrix[i, j] = idx
                idx += 1
    return index_matrix


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("main_directory", help="path to experiments folder")
    parser.add_argument("experiment_name", help="the name of the experiment for the trained net")
    parser.add_argument("checkpoint", help="version of checkpoint to load")
    args = parser.parse_args()

    experiment_name = args.experiment_name
    main_directory = args.main_directory
    checkpoint = args.checkpoint

    logger = logging.getLogger(__name__)

    tensorboard_directory = main_directory + '/runs/' + experiment_name
    writer = SummaryWriter(tensorboard_directory)

    ax = plt.axes()
    ax.set_aspect('equal', 'datalim')

    net_trained_parameters = torch.load(main_directory + '/' + experiment_name + '/' + 'checkpoint_' + str(checkpoint) + '.tar')
    for key, value in net_trained_parameters.items():
        if 'cv' in key and 'weight' in key:
            print(key)
            print(value.shape)
            index_matrix = get_idx_matrix_from_kernel(value.shape[2])
            pix_pos = cvutils.build_hexagonal_position(index_matrix)
            geom = CameraGeometry.guess(list(map(lambda x: x[0], pix_pos)) * u.m,
                                        list(map(lambda x: x[1], pix_pos)) * u.m,
                                        28 * u.m,
                                        apply_derotation=False)
            images_list = []
            for i in range(value.shape[0]):
                kernel_vec = torch.sum(value[i], 0)
                logger.info('kernel {} shape {}'.format(i, kernel_vec.shape))
                ax.clear()
                disp = CameraDisplay(geom)
                disp.image = kernel_vec.detach()
                canvas = plt.get_current_fig_manager().canvas
                canvas.draw()
                pil_img = Image.frombytes('RGB', canvas.get_width_height(), canvas.tostring_rgb())
                images_list.append(transforms.ToTensor()(pil_img))

            grid = t_utils.make_grid(images_list)

            writer.add_image('Kernel_{}'.format(key), grid, 100)


if __name__ == '__main__':
    main()
