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

import numpy
import numpy.random
import sys
from hsbk_to_rgb_display_p3 import hsbk_to_rgb_display_p3
from hsbk_to_rgb_rec2020 import hsbk_to_rgb_rec2020
from hsbk_to_rgb_srgb import hsbk_to_rgb_srgb
from rgb_to_hsbk_display_p3 import rgb_to_hsbk_display_p3
from rgb_to_hsbk_rec2020 import rgb_to_hsbk_rec2020
from rgb_to_hsbk_srgb import rgb_to_hsbk_srgb

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

EPSILON = 1e-6

device = 'srgb'
if len(sys.argv) >= 3 and sys.argv[1] == '--device':
  device = sys.argv[2]
  del sys.argv[1:3]
if len(sys.argv) < 3:
  print(f'usage: {sys.argv[0]:s} [--device device] seed count [kelv]')
  print('device in {srgb, display_p3, rec2020}, default srgb')
  print('checks invertibility of the RGB -> HSBK -> RGB pipeline')
  sys.exit(EXIT_FAILURE)
seed = int(sys.argv[1])
count = int(sys.argv[2])
kelv = float(sys.argv[3]) if len(sys.argv) >= 4 else None

hsbk_to_rgb, rgb_to_hsbk = {
  'srgb': (
    hsbk_to_rgb_srgb,
    rgb_to_hsbk_srgb
  ),
  'display_p3': (
    hsbk_to_rgb_display_p3,
    rgb_to_hsbk_display_p3
  ),
  'rec2020': (
    hsbk_to_rgb_rec2020,
    rgb_to_hsbk_rec2020
  )
}[device]

numpy.random.seed(seed)
for i in range(count):
  rgb = numpy.random.random(3)
  hsbk = rgb_to_hsbk(rgb, kelv)
  rgb1 = hsbk_to_rgb(hsbk)
  assert numpy.all(numpy.abs(rgb1 - rgb) < EPSILON)
