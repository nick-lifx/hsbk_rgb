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
from hsbk_to_rgb import hsbk_to_rgb
from rgb_to_hsbk import rgb_to_hsbk

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

EPSILON = 1e-6

if len(sys.argv) < 3:
  print(f'usage: {sys.argv[0]:s} seed count [kelv]')
  print('checks invertibility of the RGB -> HSBK -> RGB pipeline')
  sys.exit(EXIT_FAILURE)
seed = int(sys.argv[1])
count = int(sys.argv[2])
kelv = float(sys.argv[3]) if len(sys.argv) >= 4 else None

numpy.random.seed(seed)
for i in range(count):
  rgb = numpy.random.random(3)
  hsbk = rgb_to_hsbk(rgb, kelv)
  rgb1 = hsbk_to_rgb(hsbk)
  assert numpy.all(numpy.abs(rgb1 - rgb) < EPSILON)
