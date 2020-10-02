#!/usr/bin/env python3

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
