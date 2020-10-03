#!/usr/bin/env python3

import imageio
import numpy
import sys
from gamma_decode import gamma_decode
from hsbk_to_rgb import hsbk_to_rgb

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

RGB_RED = 0
RGB_GREEN = 1
RGB_BLUE = 2
N_RGB = 3

UVW_U = 0
UVW_V = 1
UVW_W = 2
N_UVW = 3

EPSILON = 1e-6

# inverse of the matrix calculated by ../prepare/UVW_to_rgb.py
rgb_to_UVW = numpy.array(
  [
    [0.0904510486390004, 0.0784301651048639, 0.0395854529228023],
    [0.0699582329317269, 0.235290495314592, 0.0237512717536814],
    [0.0402789825970549, 0.313720660419456, 0.16230035698349]
  ],
  numpy.double
)

if len(sys.argv) < 2:
  print(f'usage: {sys.argv[0]:s} image_out')
  print('image_out = name of PNG file to create (will be overwritten)')
  print('creates 361 x 376 x 3 image with 0..360 degrees by 1, 1500..9000 Kelvin by 20')
  sys.exit(EXIT_FAILURE)
image_out = sys.argv[1]

def hsbk_to_uv(hsbk):
  rgb = hsbk_to_rgb(hsbk)
  for i in range(N_RGB):
    rgb[i] = gamma_decode(rgb[i])
  UVW = rgb_to_UVW @ rgb
  return UVW[:UVW_W] / numpy.sum(UVW)

# find chromaticities of the hue space by 1 degree increments
hue_uv = numpy.stack(
  [
    hsbk_to_uv(numpy.array([1. * i, 1., 1., 6504.], numpy.double))
    for i in range(361)
  ],
  0
)

# find chromaticities of the Kelvin space by 20 degree increments
kelv_uv = numpy.stack(
  [
    hsbk_to_uv(numpy.array([0., 0., 1., 1500. + 20. * i], numpy.double))
    for i in range(376)
  ],
  0
)

# find chromaticities of the hue x Kelvin space @ saturation .5, then
# convert each chromaticity to a weighting between hue_uv and kelv_uv
image = numpy.zeros((376, 361), numpy.double)
for i in range(376):
  print(i, '/', 376)
  kelv = 1500. + 20. * i
  v0 = kelv_uv[i, :]
  for j in range(361):
    hue = 1. * j
    v1 = hue_uv[j, :] - v0
    uv = hsbk_to_uv(numpy.array([hue, .5, 1., kelv], numpy.double))
    w = ((uv - v0) @ v1) / (v1 @ v1)
    if w < 0.:
      w = 0.
    elif w > 1.:
      w = 1.
    image[i, j] = w

imageio.imwrite(image_out, numpy.round(image * 255.).astype(numpy.uint8))
