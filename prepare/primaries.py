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
import numpy.linalg
import ruamel.yaml
import sys
from numpy_to_python import numpy_to_python
from python_to_numpy import python_to_numpy

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

RGB_RED = 0
RGB_GREEN = 1
RGB_BLUE = 2
N_RGB = 3

RGBW_RED = 0
RGBW_GREEN = 1
RGBW_BLUE = 2
RGBW_WHITE = 3
N_RGBW = 4

UVL_u = 0
UVL_v = 1
UVL_L = 2
N_UVL = 3

UVW_U = 0
UVW_V = 1
UVW_W = 2
N_UVW = 3

XY_x = 0
XY_y = 1
N_XY = 2

XYZ_X = 0
XYZ_Y = 1
XYZ_Z = 2
N_XYZ = 3

# see https://en.wikipedia.org/wiki/CIE_1960_color_space
XYZ_to_UVW = numpy.array(
  [
    [2. / 3., 0., 0.],
    [0., 1., 0.],
    [-1. / 2., 3. / 2, 1. / 2.]
  ],
  numpy.double
)
UVW_to_XYZ = numpy.array(
  [
    [3. / 2., 0., 0.],
    [0., 1., 0.],
    [3. / 2., -3., 2.]
  ],
  numpy.double
)

if len(sys.argv) < 3:
  print(f'usage: {sys.argv[0]:s} rgbw_to_xy_in.yml primaries_out.yml')
  sys.exit(EXIT_FAILURE)
rgbw_to_xy_in = sys.argv[1]
primaries_out = sys.argv[2]

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

# scale R, G, B by those factors so primaries sum to white point, discard white point
rgb_to_XYZ = rgbw_to_XYZ[:, :RGBW_WHITE] * x[numpy.newaxis, :]

# convert from (X, Y, Z) system to more perceptually uniform (U, V, W) system
rgb_to_UVW = XYZ_to_UVW @ rgb_to_XYZ

# create inverse versions
XYZ_to_rgb = numpy.linalg.inv(rgb_to_XYZ)
UVW_to_rgb = XYZ_to_rgb @ UVW_to_XYZ

# create special versions in which L = X + Y + Z or L = U + V + W
# this makes it easier to convert xy <-> RGB or uv <-> RGB directly
XYZ_to_XYL = UVW_to_UVL = numpy.array(
  [
    [1., 0., 0.],
    [0., 1., 0.],
    [1., 1., 1.]
  ],
  numpy.double
)
XYL_to_XYZ = UVL_to_UVW = numpy.array(
  [
    [1., 0., 0.],
    [0., 1., 0.],
    [-1., -1., 1.]
  ],
  numpy.double
)
rgb_to_XYL = XYZ_to_XYL @ rgb_to_XYZ
XYL_to_rgb = XYZ_to_rgb @ XYL_to_XYZ
rgb_to_UVL = UVW_to_UVL @ rgb_to_UVW
UVL_to_rgb = UVW_to_rgb @ UVL_to_UVW

primaries = {
  'rgb_to_XYZ': rgb_to_XYZ,
  'XYZ_to_rgb': XYZ_to_rgb,
  'rgb_to_UVW': rgb_to_UVW,
  'UVW_to_rgb': UVW_to_rgb,
  'rgb_to_XYL': rgb_to_XYL,
  'XYL_to_rgb': XYL_to_rgb,
  'rgb_to_UVL': rgb_to_UVL,
  'UVL_to_rgb': UVL_to_rgb
}
with open(primaries_out, 'w') as fout:
  yaml.dump(numpy_to_python(primaries), fout)
