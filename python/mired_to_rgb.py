#!/usr/bin/env python3
# generated by ../prepare/mired_to_rgb_gen_py.py

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

EPSILON = 1e-6

def mired_to_rgb(mired):
  # validate inputs, allowing a little slack
  assert mired >= 6.6666666666666671e+01 - EPSILON
  assert mired < 1.0000000000000000e+03 + EPSILON

  # calculate red channel
  if mired < 1.5301383549813977e+02:
    r = 3.9570969341012815e-09
    r = r * mired + 8.8076156789567395e-06
    r = r * mired + 1.2887035144926798e-03
    r = r * mired + 5.8241927431124185e-01
  else:
    r = 1.0000000000000000e+00

  # calculate green channel
  if mired < 1.5338754503022363e+02:
    g = -3.2321841543747237e-09
    g = g * mired + 5.6229842258377055e-06
    g = g * mired + 1.0736686414387880e-03
    g = g * mired + 6.9132967045390203e-01
  else:
    g = -2.8970767314178409e-15
    g = g * mired + 7.5119014692025205e-12
    g = g * mired + -8.1334265621981482e-09
    g = g * mired + 5.1275967863145201e-06
    g = g * mired + -2.8328853318459139e-03
    g = g * mired + 1.3159773875623144e+00

  # calculate blue channel
  if mired < 1.5270014407627858e+02:
    b = 1.0000000000000000e+00
  elif mired < 5.2600074995195587e+02:
    b = -1.1645892018287090e-18
    b = b * mired + 7.1965968414243118e-16
    b = b * mired + 1.1933670300759820e-12
    b = b * mired + -1.6068394829417969e-09
    b = b * mired + 7.8016086297614117e-07
    b = b * mired + -1.8092627635589906e-04
    b = b * mired + 1.6060024299104789e-02
    b = b * mired + 7.5623044541563855e-01
  else:
    b = 0.0000000000000000e+00

  return numpy.array([r, g, b], numpy.double)

if __name__ == '__main__':
  import sys

  EXIT_SUCCESS = 0
  EXIT_FAILURE = 1

  RGB_RED = 0
  RGB_GREEN = 1
  RGB_BLUE = 2
  N_RGB = 3

  if len(sys.argv) < 2:
    print(f'usage: {sys.argv[0]:s} mired')
    print('mired = colour temperature in micro reciprocal degrees Kelvin')
    sys.exit(EXIT_FAILURE)
  mired = float(sys.argv[1])

  rgb = mired_to_rgb(mired)
  print(
    f'mired {mired:.3f} -> RGB ({rgb[RGB_RED]:.6f}, {rgb[RGB_GREEN]:.6f}, {rgb[RGB_BLUE]:.6f})'
  )
