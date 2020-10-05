#!/usr/bin/env python3

# Copyright (c) 2020 Nick Downing
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
    [9.0451048639000400e-02, 7.8430165104863919e-02, 3.9585452922802314e-02],
    [6.9958232931726871e-02, 2.3529049531459176e-01, 2.3751271753681389e-02],
    [4.0278982597054855e-02, 3.1372066041945568e-01, 1.6230035698348952e-01]
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
