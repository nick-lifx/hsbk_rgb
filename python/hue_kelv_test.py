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
from hsbk_to_rgb import hsbk_to_rgb

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

EPSILON = 1e-6

if len(sys.argv) < 4:
  print(f'usage: {sys.argv[0]:s} sat br image_out')
  print('sat = saturation as fraction (0 to 1)')
  print('br = brightness as fraction (0 to 1)')
  print('image_out = name of PNG file to create (will be overwritten)')
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
