#!/usr/bin/env python3

import imageio
import numpy
import sys
from hsbk_to_rgb import hsbk_to_rgb
from rgb_to_hsbk import rgb_to_hsbk

rgb_to_UVW = numpy.array(
  [
    [0.09045105, 0.07843017, 0.03958545],
    [0.06995823, 0.23529050, 0.02375127],
    [0.04027898, 0.31372066, 0.16230036]
  ],
  numpy.double
)

EPSILON = 1e-6

EXIT_FAILURE = 1

if len(sys.argv) < 4:
  print(f'usage: {sys.argv[0]:s} sat br image_out')
  print('image_out = name of .jpg or .png file to create (will be overwritten)')
  print('creates 361 x 376 x 3 image with 0..360 degrees by 1, 1500..9000 Kelvin by 20')
  sys.exit(EXIT_FAILURE)
sat = float(sys.argv[1])
br = float(sys.argv[2])
image_out = sys.argv[3]

image = numpy.zeros((376, 361, 3), numpy.double)
for i in range(376):
  print(i, '/', 376)
  kelv = 1500. + 20. * i
  for j in range(361):
    hue = 1. * j
    image[i, j, :] = hsbk_to_rgb(
      numpy.array([hue, sat, br, kelv], numpy.double)
    )
imageio.imwrite(image_out, numpy.round(image * 255.).astype(numpy.uint8))
