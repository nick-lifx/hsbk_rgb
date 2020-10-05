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

import math
import numpy
import sys

EPSILON = 1e-6

def kelv_to_uv(kelv):
  # validate inputs, allowing a little slack
  assert kelv >= 1000. - EPSILON and kelv < 15000. + EPSILON

  # find the approximate (u, v) chromaticity of the given Kelvin value
  # see http://en.wikipedia.org/wiki/Planckian_locus#Approximation (Krystek)
  # we evaluate this with Horner's rule for better numerical stability
  u = 1.28641212e-7
  u = u * kelv + 1.54118254e-4
  u = u * kelv + .860117757
  u_denom = 7.08145163e-7
  u_denom = u_denom * kelv + 8.42420235e-4
  u_denom = u_denom * kelv + 1.
  u /= u_denom

  v = 4.20481691e-8
  v = v * kelv + 4.22806245e-5
  v = v * kelv + .317398726
  v_denom = 1.61456053e-7
  v_denom = v_denom * kelv - 2.89741816e-5
  v_denom = v_denom * kelv + 1.
  v /= v_denom

  return numpy.array([u, v], numpy.double)

if __name__ == '__main__':
  import sys

  EXIT_SUCCESS = 0
  EXIT_FAILURE = 1

  UV_u = 0
  UV_v = 1
  N_UV = 2

  if len(sys.argv) < 2:
    print(f'usage: {sys.argv[0]:s} kelv')
    print('kelv = colour temperature in degrees Kelvin')
    sys.exit(EXIT_FAILURE)
  kelv = float(sys.argv[1])

  uv = kelv_to_uv(kelv)
  print(
    f'kelv {kelv:.3f} -> uv ({uv[UV_u]:.6f}, {uv[UV_v]:.6f})'
  )
