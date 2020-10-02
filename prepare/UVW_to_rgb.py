#!/usr/bin/env python3

import numpy
import numpy.linalg
import ruamel.yaml
import sys
from numpy_to_python import numpy_to_python
from python_to_numpy import python_to_numpy

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

RGBW_RED = 0
RGBW_GREEN = 1
RGBW_BLUE = 2
RGBW_WHITE = 3
N_RGBW = 4

XY_x = 0
XY_y = 1
N_XY = 2

# see https://en.wikipedia.org/wiki/CIE_1960_color_space
XYZ_to_UVW = numpy.array(
  [
    [2. / 3., 0., 0.],
    [0., 1., 0.],
    [-1. / 2., 3. / 2, 1. / 2.]
  ],
  numpy.double
)

if len(sys.argv) < 3:
  print(f'usage: {sys.argv[0]:s} rgbw_to_xy_in.yml UVW_to_rgb_out.yml')
  sys.exit(EXIT_FAILURE)
rgbw_to_xy_in = sys.argv[1]
UVW_to_rgb_out = sys.argv[2]

yaml = ruamel.yaml.YAML(typ = 'safe')
#numpy.set_printoptions(threshold = numpy.inf)

# these contain the published (x, y) primaries of the SRGB system
# see https://en.wikipedia.org/wiki/SRGB
# across is R, G, B, W and down is x, y
# the last one is not actually a primary but the so-called white point
# this means that R + G + B all at full intensity should make the given (x, y)
with open(rgbw_to_xy_in) as fin:
  rgbw_to_xy = python_to_numpy(yaml.load(fin))

# add the missing z row, to convert the primaries from (x, y) to (X, Y, Z)
# see https://en.wikipedia.org/wiki/CIE_1931_color_space#CIE_xy_chromaticity_diagram_and_the_CIE_xyY_color_space
x = rgbw_to_xy[XY_x, :]
y = rgbw_to_xy[XY_y, :]
rgbw_to_XYZ = numpy.stack([x, y, 1. - x - y], 0)

# find the linear combination of R, G, B primaries to make the white point
x = numpy.linalg.solve(
  rgbw_to_XYZ[:, :RGBW_WHITE],
  rgbw_to_XYZ[:, RGBW_WHITE]
)

# then scale R, G, B by those factors so the primaries sum to the white point
# at this point the white point is not needed any more, so trim it off
rgb_to_XYZ = rgbw_to_XYZ[:, :RGBW_WHITE] * x[numpy.newaxis, :]

# and finally convert from the (X, Y, Z) system to the (U, V, W) system
rgb_to_UVW = XYZ_to_UVW @ rgb_to_XYZ

# we want to convert Kelvin -> (u, v) -> (U, V, W) -> (R, G, B)
# to make this as easy as possible we invert the above-calculated matrix
UVW_to_rgb = numpy.linalg.inv(rgb_to_UVW)

with open(UVW_to_rgb_out, 'w') as fout:
  yaml.dump(numpy_to_python(UVW_to_rgb), fout)
