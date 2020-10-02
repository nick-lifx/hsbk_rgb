#!/usr/bin/env python3

import imageio
import numpy
import sys
from hsbk_to_rgb import hsbk_to_rgb
from rgb_to_hsbk import rgb_to_hsbk

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

HSBK_HUE = 0
HSBK_SAT = 1
HSBK_BR = 2
HSBK_KELV = 3
N_HSBK = 4

EPSILON = 1e-6

if len(sys.argv) < 4:
  print(f'usage: {sys.argv[0]:s} image_in kelv image_out')
  print('image_in = name of .jpg or .png file to read')
  print('kelv = implicit colour temperature to apply to HSV pixels, in degrees Kelvin')
  print('image_out = name of .png file (HSV pixels) to create (will be overwritten)')
  sys.exit(EXIT_FAILURE)
image_in = sys.argv[1]
kelv = float(sys.argv[2])
image_out = sys.argv[3]

image = imageio.imread(image_in).astype(numpy.double) / 255.
assert len(image.shape) == 3 and image.shape[2] == 3
y_size, x_size, _ = image.shape

for i in range(y_size):
  print(i, '/', y_size)
  for j in range(x_size):
    image[i, j, :] = rgb_to_hsbk(image[i, j, :], kelv)[:HSBK_KELV]

imageio.imwrite(
  image_out,
  numpy.round(
    image * numpy.array(
      [256. / 360., 255., 255.],
      numpy.double
    )[numpy.newaxis, numpy.newaxis, :]
  ).astype(numpy.uint8)
)
