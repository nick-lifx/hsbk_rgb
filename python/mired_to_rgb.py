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
  assert mired >= 6.6666666666666671e+01 - EPSILON and mired < 1.0000000000000000e+03 + EPSILON

  # calculate red channel
  if mired < 1.5301124013313614e+02:
    r = 4.0759697335497374e-09
    r = r * mired + 8.7745352040474616e-06
    r = r * mired + 1.2915084602695970e-03
    r = r * mired + 5.8234979620914951e-01
  else:
    r = 1.0000000000000000e+00

  # calculate green channel
  if mired < 1.5328014096506672e+02:
    g = -3.1788989850789769e-09
    g = g * mired + 5.6167093228645755e-06
    g = g * mired + 1.0730450836593918e-03
    g = g * mired + 6.9139743473566284e-01
  else:
    g = -3.2061721036029189e-15
    g = g * mired + 8.3177466244160031e-12
    g = g * mired + -8.8963302229775505e-09
    g = g * mired + 5.4444099765204752e-06
    g = g * mired + -2.8874311235000962e-03
    g = g * mired + 1.3187778684669054e+00

  # calculate blue channel
  if mired < 1.5299152140823011e+02:
    b = 1.0000000000000000e+00
  elif mired < 5.2654870870753894e+02:
    b = 4.3598326332997760e-18
    b = b * mired + -1.2026137133965763e-14
    b = b * mired + 1.3430761955540394e-11
    b = b * mired + -7.9267669229309758e-09
    b = b * mired + 2.6707692102215032e-06
    b = b * mired + -5.0764325023218632e-04
    b = b * mired + 4.6190379896779578e-02
    b = b * mired + -3.8592645578185092e-01
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
