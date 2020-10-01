#!/usr/bin/env python3

import numpy
import numpy.random
import sys
from hsbk_to_rgb import hsbk_to_rgb
from rgb_to_hsbk import rgb_to_hsbk

EPSILON = 1e-6

EXIT_FAILURE = 1

if len(sys.argv) < 3:
  print(f'usage: {sys.argv[0]:s} seed count')
  print('checks invertibility of the RGB -> HSBK -> RGB pipeline')
  sys.exit(EXIT_FAILURE)
seed = int(sys.argv[1])
count = int(sys.argv[2])

numpy.random.seed(seed)
for i in range(count):
  rgb = numpy.random.random(3)
  hsbk = rgb_to_hsbk(rgb)
  rgb1 = hsbk_to_rgb(hsbk)
  assert numpy.all(numpy.abs(rgb - rgb1) < EPSILON)
