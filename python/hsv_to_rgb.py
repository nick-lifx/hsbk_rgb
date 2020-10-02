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

if len(sys.argv) < 3:
  print(f'usage: {sys.argv[0]:s} image_in image_out [kelv]')
  print('image_in = name of PNG file (HSV pixels) to read')
  print('image_out = name of PNG file to create (will be overwritten)')
  print('kelv = implicit colour temperature to apply to HSV pixels (default 6504K)')
  sys.exit(EXIT_FAILURE)
image_in = sys.argv[1]
image_out = sys.argv[2]
kelv = float(sys.argv[3]) if len(sys.argv) >= 4 else 6504.

image = imageio.imread(image_in).astype(numpy.double) / numpy.array(
  [256. / 360., 255., 255.],
  numpy.double
)[numpy.newaxis, numpy.newaxis, :]
assert len(image.shape) == 3 and image.shape[2] == 3
y_size, x_size, _ = image.shape

for i in range(y_size):
  print(i, '/', y_size)
  for j in range(x_size):
    image[i, j, :] = hsbk_to_rgb(
      numpy.concatenate(
        [image[i, j, :], numpy.array([kelv], numpy.double)],
        0
      )
    )
imageio.imwrite(image_out, numpy.round(image * 255.).astype(numpy.uint8))
