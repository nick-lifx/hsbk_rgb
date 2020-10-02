#!/usr/bin/env python3

import imageio
import numpy
import sys
from hsbk_to_rgb import hsbk_to_rgb
from rgb_to_hsbk import rgb_to_hsbk

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

EPSILON = 1e-6

rgb_to_UVW = numpy.array(
  [
    [0.09045105, 0.07843017, 0.03958545],
    [0.06995823, 0.23529050, 0.02375127],
    [0.04027898, 0.31372066, 0.16230036]
  ],
  numpy.double
)

if len(sys.argv) < 2:
  print(f'usage: {sys.argv[0]:s} image_out')
  print('image_out = name of .jpg or .png file to create (will be overwritten)')
  print('creates 361 x 376 x 3 image with 0..360 degrees by 1, 1500..9000 Kelvin by 20')
  sys.exit(EXIT_FAILURE)
image_out = sys.argv[1]

# find chromaticities of the hue space by 1 degree increments
hue_UVW = rgb_to_UVW @ numpy.stack(
  [
    hsbk_to_rgb(numpy.array([1. * i, 1., 1., 6504.], numpy.double))
    for i in range(361)
  ],
  1
)
hue_uv = hue_UVW[:2, :] / hue_UVW[2:, :]

# find chromaticities of the Kelvin space by 20 degree increments
kelv_UVW = rgb_to_UVW @ numpy.stack(
  [
    hsbk_to_rgb(numpy.array([0., 0., 1., 1500. + 20. * i], numpy.double))
    for i in range(376)
  ],
  1
)
kelv_uv = kelv_UVW[:2, :] / kelv_UVW[2:, :]

# find chromaticities of the hue x Kelvin space @ saturation .5, then
# convert each chromaticity to a weighting between hue_uv and kelv_uv
image = numpy.zeros((376, 361), numpy.double)
for i in range(376):
  print(i, '/', 376)
  kelv = 1500. + 20. * i
  v0 = kelv_uv[:, i]
  for j in range(361):
    hue = 1. * j
    rgb = hsbk_to_rgb(numpy.array([hue, .5, 1., kelv], numpy.double))
    mask = rgb < 12.92 * .0031308
    rgb[mask] /= 12.92
    rgb[~mask] = ((rgb[~mask] + .055) / 1.055) ** 2.4
    UVW = rgb_to_UVW @ rgb
    uv = UVW[:2] / UVW[2]
    v1 = hue_uv[:, j] - v0
    image[i, j] = ((uv - v0) @ v1) / (v1 @ v1)

# due to the corruption of chromaticities that occurs when hue and
# Kelvin get combined, the weighting factor can be outside [0, 1]
image[image < 0.] = 0.
image[image > 1.] = 1.

imageio.imwrite(image_out, numpy.round(image * 255.).astype(numpy.uint8))
