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

RGB_RED = 0
RGB_GREEN = 1
RGB_BLUE = 2
N_RGB = 3

UVW_U = 0
UVW_V = 1
UVW_W = 2
N_UVW = 3

UVL_u = 0
UVL_v = 1
UVL_L = 2
N_UVL = 3

EPSILON = 1e-6

#numpy.set_printoptions(threshold = numpy.inf)

if len(sys.argv) < 3:
  print(f'usage: {sys.argv[0]:s} model_in.yml red,green,blue')
  sys.exit(1)
model_in = sys.argv[1]
rgb0 = numpy.array([float(i) for i in sys.argv[2].split(',')], numpy.double)

assert rgb0.shape[0] == N_RGB

model = utils.yaml_io._import(utils.yaml_io.read_file(model_in))
gamma_a = model['gamma_a']
gamma_b = model['gamma_b']
gamma_c = model['gamma_c']
gamma_d = model['gamma_d']
gamma_e = model['gamma_e']
primaries_uvL = model['primaries_uvL']

# calculate normalized UVW vectors for the primaries
u = primaries_uvL[:, UVL_u]
v = primaries_uvL[:, UVL_v]
primaries_UVW = numpy.stack([u, v, 1. - u - v], 1)

# gamma-decode
mask = rgb0 >= gamma_a * gamma_b
rgb1 = numpy.zeros_like(rgb0)
rgb1[~mask] = rgb0[~mask] / gamma_a
rgb1[mask] = ((rgb0[mask] + gamma_c) / gamma_d) ** gamma_e

UVW = rgb1 @ primaries_UVW
U = UVW[UVW_U]
V = UVW[UVW_V]
L = numpy.sum(UVW)
uvL = numpy.array([U / L, V / L, L], numpy.double)

print(
  f'rgb ({rgb0[RGB_RED]:.6f}, {rgb0[RGB_GREEN]:.6f}, {rgb0[RGB_BLUE]:.6f}) -> uvL ({uvL[UVL_u]:.6f}, {uvL[UVL_v]:.6f}, {uvL[UVL_L]:.6f})'
)
