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

# put utils into path
# temporary until we have proper Python packaging
import os.path
import sys
dirname = os.path.dirname(__file__)
sys.path.append(os.path.join(dirname, '..'))

import numpy
import numpy.linalg
import utils.yaml_io

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

UVW_U = 0
UVW_V = 1
UVW_W = 2
N_UVW = 3

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

#numpy.set_printoptions(threshold = numpy.inf)

if len(sys.argv) < 8:
  print(f'usage: {sys.argv[0]:s} a b c d e rgbw_to_xy_in.yml model_out.yml')
  print('gamma decode function is:')
  print('  y = x / a if x < a * b else ((x + c) / d) ** e')
  print('gamma encode function is:')
  print('  x = y * a if y < b else (y ** (1. / e) * d) - c')
  sys.exit(EXIT_FAILURE)
gamma_a = float(sys.argv[1])
gamma_b = float(sys.argv[2])
gamma_c = float(sys.argv[3])
gamma_d = float(sys.argv[4])
gamma_e = float(sys.argv[5])
rgbw_to_xy_in = sys.argv[6]
model_out = sys.argv[7]

# contains the published (x, y) primaries of the SRGB (or other) system
# see https://en.wikipedia.org/wiki/SRGB
# across is R, G, B, W and down is x, y
# the last one is not actually a primary but the so-called white point
# this means that R + G + B all at full intensity should make the given (x, y)
rgbw_to_xy = utils.yaml_io._import(utils.yaml_io.read_file(rgbw_to_xy_in))

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

# scale R, G, B by this so primaries sum to white point, discard white point
rgb_to_XYZ = rgbw_to_XYZ[:, :RGBW_WHITE] * x[numpy.newaxis, :]

# convert from (X, Y, Z) system to more perceptually uniform (U, V, W) system
rgb_to_UVW = XYZ_to_UVW @ rgb_to_XYZ

# transpose and save as (u, v, L) where L = U + V + W is proxy for intensity
U = rgb_to_UVW[UVW_U, :]
V = rgb_to_UVW[UVW_V, :]
L = numpy.sum(rgb_to_UVW, 0)
primaries_uvL = numpy.stack([U / L, V / L, L], 1)

utils.yaml_io.write_file(
  model_out,
  utils.yaml_io.export(
    {
      'gamma_a': gamma_a,
      'gamma_b': gamma_b,
      'gamma_c': gamma_c,
      'gamma_d': gamma_d,
      'gamma_e': gamma_e,
      'primaries_uvL': primaries_uvL
    }
  )
)
