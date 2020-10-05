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

def kelv_to_uv_deriv(kelv):
  # validate inputs, allowing a little slack
  assert kelv >= 1000. - EPSILON and kelv < 15000. + EPSILON

  # find the approximate (u, v) chromaticity of the given Kelvin value
  # see http://en.wikipedia.org/wiki/Planckian_locus#Approximation (Krystek)
  # we evaluate this with Horner's rule for better numerical stability
  u_num = 1.28641212e-7
  u_num = u_num * kelv + 1.54118254e-4
  u_num = u_num * kelv + .860117757

  u_num_deriv = 1.28641212e-7 * 2.
  u_num_deriv = u_num_deriv * kelv + 1.54118254e-4

  u_denom = 7.08145163e-7
  u_denom = u_denom * kelv + 8.42420235e-4
  u_denom = u_denom * kelv + 1.

  u_denom_deriv = 7.08145163e-7 * 2.
  u_denom_deriv = u_denom_deriv * kelv + 8.42420235e-4
 
  v_num = 4.20481691e-8
  v_num = v_num * kelv + 4.22806245e-5
  v_num = v_num * kelv + .317398726

  v_num_deriv = 4.20481691e-8 * 2.
  v_num_deriv = v_num_deriv * kelv + 4.22806245e-5
 
  v_denom = 1.61456053e-7
  v_denom = v_denom * kelv - 2.89741816e-5
  v_denom = v_denom * kelv + 1.

  v_denom_deriv = 1.61456053e-7 * 2.
  v_denom_deriv = v_denom_deriv * kelv - 2.89741816e-5

  uv_num = numpy.array([u_num, v_num], numpy.double)
  uv_denom = numpy.array([u_denom, v_denom], numpy.double)
  uv_num_deriv = numpy.array([u_num_deriv, v_num_deriv], numpy.double)
  uv_denom_deriv = numpy.array([u_denom_deriv, v_denom_deriv], numpy.double)

  # quotient rule for differentiation
  return (
    (uv_num_deriv * uv_denom - uv_num * uv_denom_deriv) / (uv_denom ** 2),
    uv_num / uv_denom
  )

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

  uv_deriv, _ = kelv_to_uv_deriv(kelv)
  print(
    f'kelv {kelv:.3f} -> u\'v\' ({uv_deriv[UV_u]:.12f}, {uv_deriv[UV_v]:.12f})'
  )
