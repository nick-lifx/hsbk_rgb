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
from hsbk_to_rgb_display_p3 import hsbk_to_rgb_display_p3
from hsbk_to_rgb_srgb import hsbk_to_rgb_srgb

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

HSBK_HUE = 0
HSBK_SAT = 1
HSBK_BR = 2
HSBK_KELV = 3
N_HSBK = 4

EPSILON = 1e-6

device = 'srgb'
if len(sys.argv) >= 3 and sys.argv[1] == '--device':
  device = sys.argv[2]
  del sys.argv[1:3]
if len(sys.argv) < 3:
  print(f'usage: {sys.argv[0]:s} [--device device] image_in image_out [kelv]')
  print('device in {srgb, display_p3}, default srgb')
  print('image_in = name of PNG file (HSV pixels) to read')
  print('image_out = name of PNG file to create (will be overwritten)')
  print('kelv = implicit colour temperature to apply to HSV pixels (default 6504K)')
  sys.exit(EXIT_FAILURE)
image_in = sys.argv[1]
image_out = sys.argv[2]
kelv = float(sys.argv[3]) if len(sys.argv) >= 4 else 6504.

hsbk_to_rgb = {
  'srgb': hsbk_to_rgb_srgb,
  'display_p3': hsbk_to_rgb_display_p3
}[device]

image = imageio.imread(image_in).astype(numpy.double) / numpy.array(
  [256. / 360., 255., 255.],
  numpy.double
)[numpy.newaxis, numpy.newaxis, :]
assert len(image.shape) == 3 and image.shape[2] == 3
y_size, x_size, _ = image.shape

for i in range(y_size):
  print(i, '/', y_size)
  for j in range(x_size):
    image[i, j, :] = hsbk_to_rgb.convert(
      numpy.concatenate(
        [image[i, j, :], numpy.array([kelv], numpy.double)],
        0
      )
    )
imageio.imwrite(image_out, numpy.round(image * 255.).astype(numpy.uint8))
