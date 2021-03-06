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
import utils.yaml_io

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

RGB_RED = 0
RGB_GREEN = 1
RGB_BLUE = 2
N_RGB = 3

UVL_U = 0
UVL_u = 0
UVL_V = 1
UVL_v = 1
UVL_L = 2
N_UVL = 3

#numpy.set_printoptions(threshold = numpy.inf)

if len(sys.argv) < 4:
  print(f'usage: {sys.argv[0]:s} model_in.yml gamma_curve device')
  sys.exit(EXIT_FAILURE)
model_in = sys.argv[1]
gamma_curve = sys.argv[2]
device = sys.argv[3]

model = utils.yaml_io._import(utils.yaml_io.read_file(model_in))
primaries_uvL = model['primaries_uvL']

u = primaries_uvL[:, UVL_u]
v = primaries_uvL[:, UVL_v]
L = primaries_uvL[:, UVL_L]
primaries_UVW = numpy.stack([u, v, 1. - u - v], 1) * L[:, numpy.newaxis]

# create a special version in which L = U + V + W
# this makes it easier to convert uv <-> RGB directly
# note: UVL differs from uvL as U, V are scaled by the L
rgb_to_UVL = numpy.array(
  [
    [1., 0., 0.],
    [0., 1., 0.],
    [1., 1., 1.]
  ],
  numpy.double
) @ primaries_UVW.transpose()
UVL_to_rgb = numpy.linalg.inv(rgb_to_UVL)

sys.stdout.write(
  sys.stdin.read().format(
    gamma_curve = gamma_curve,
    device = device,
    UVL_to_rgb = f'''
      [{UVL_to_rgb[RGB_RED, UVL_U]:.16e}, {UVL_to_rgb[RGB_RED, UVL_V]:.16e}, {UVL_to_rgb[RGB_RED, UVL_L]:.16e}],
      [{UVL_to_rgb[RGB_GREEN, UVL_U]:.16e}, {UVL_to_rgb[RGB_GREEN, UVL_V]:.16e}, {UVL_to_rgb[RGB_GREEN, UVL_L]:.16e}],
      [{UVL_to_rgb[RGB_BLUE, UVL_U]:.16e}, {UVL_to_rgb[RGB_BLUE, UVL_V]:.16e}, {UVL_to_rgb[RGB_BLUE, UVL_L]:.16e}]'''
  )

)
