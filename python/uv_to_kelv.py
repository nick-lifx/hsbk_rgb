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
from kelv_to_uv_deriv import kelv_to_uv_deriv

UV_u = 0
UV_v = 1
N_UV = 2

XY_x = 0
XY_y = 1
N_XY = 2

EPSILON = 1e-6

def uv_to_kelv(uv):
  # validate inputs, allowing a little slack
  assert numpy.all(uv >= -EPSILON) and numpy.sum(uv) < 1. + EPSILON

  # convert to xy for McCamy's approximation
  # see https://en.wikipedia.org/wiki/CIE_1960_color_space#Relation_to_CIE_XYZ
  xy = (
    uv * numpy.array([3., 2.], numpy.double) /
      (uv @ numpy.array([2., -8.], numpy.double) + 4)
  )
  #print('xy', xy)
  assert xy[XY_y] >= .1858 + EPSILON

  # make initial estimate by McCamy's approximation
  # see https://en.wikipedia.org/wiki/Color_temperature#Approximation
  # does not work well below 1500K, but the loop below can recover OK
  n = (xy[XY_x] - .3320) / (xy[XY_y] - .1858)
  x = -449.
  x = x * n + 3525.
  x = x * n - 6823.3
  x = x * n + 5520.33
  #print('x', x)

  # refine initial estimate with Newton's method
  i = 0
  while True:
    if x < 1000.:
      x = 1000.
    elif x > 15000.:
      x = 15000.
    y_deriv, y = kelv_to_uv_deriv(x)
    y_to_uv = uv - y
    #print('i', i, 'x', x, 'y', y, 'y_deriv', y_deriv, 'y_to_uv', y_to_uv)
    if i >= 5:
      break
    x += (y_deriv @ y_to_uv) / (y_deriv @ y_deriv)
    i += 1

  y_normal = numpy.array([-y_deriv[UV_v], y_deriv[UV_u]], numpy.double)
  y_normal /= math.sqrt(numpy.sum(numpy.square(y_normal)))
  return x, y, y_to_uv @ y_normal # duv

if __name__ == '__main__':
  import sys

  EXIT_SUCCESS = 0
  EXIT_FAILURE = 1

  if len(sys.argv) < 3:
    print(f'usage: {sys.argv[0]:s} u v')
    print('u = CIE 1960 u coordinate (0 to 1)')
    print('v = CIE 1960 v coordinate (0 to 1)')
    print('sum of u and v cannot exceed 1')
    sys.exit(EXIT_FAILURE)
  uv = numpy.array([float(i) for i in sys.argv[1:3]], numpy.double)

  kelv, _, duv = uv_to_kelv(uv)
  print(
    f'uv ({uv[UV_u]:.6f}, {uv[UV_v]:.6f}) -> kelv {kelv:.3f} duv {duv:.6f}'
  )
