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

MIRED_MIN = 1e6 / 15000.
MIRED_MAX = 1e6 / 1000.

class MiredToRGB:
  def __init__(
    self,
    b_red,
    b_green,
    b_blue,
    c_blue,
    p_red_ab,
    p_green_ab,
    p_green_bd,
    p_blue_bc
  ):
    # the evaluation code makes assumptions as follows:
    assert p_red_ab.shape[0] == 4
    assert p_green_ab.shape[0] == 4
    assert p_green_bd.shape[0] == 6
    assert p_blue_bc.shape[0] == 8

    self.b_red = b_red
    self.b_green = b_green
    self.b_blue = b_blue
    self.c_blue = c_blue
    self.p_red_ab = p_red_ab
    self.p_green_ab = p_green_ab
    self.p_green_bd = p_green_bd
    self.p_blue_bc = p_blue_bc

  def convert(self, mired):
    # validate inputs, allowing a little slack
    assert mired >= MIRED_MIN - EPSILON and mired < MIRED_MAX + EPSILON

    # calculate red channel
    if mired < self.b_red:
      r = self.p_red_ab[3]
      r = r * mired + self.p_red_ab[2]
      r = r * mired + self.p_red_ab[1]
      r = r * mired + self.p_red_ab[0]
    else:
      r = 1.

    # calculate green channel
    if mired < self.b_green:
      g = self.p_green_ab[3]
      g = g * mired + self.p_green_ab[2]
      g = g * mired + self.p_green_ab[1]
      g = g * mired + self.p_green_ab[0]
    else:
      g = self.p_green_bd[5]
      g = g * mired + self.p_green_bd[4]
      g = g * mired + self.p_green_bd[3]
      g = g * mired + self.p_green_bd[2]
      g = g * mired + self.p_green_bd[1]
      g = g * mired + self.p_green_bd[0]

    # calculate blue channel
    if mired < self.b_blue:
      b = 1.
    elif mired < self.c_blue:
      b = self.p_blue_bc[7]
      b = b * mired + self.p_blue_bc[6]
      b = b * mired + self.p_blue_bc[5]
      b = b * mired + self.p_blue_bc[4]
      b = b * mired + self.p_blue_bc[3]
      b = b * mired + self.p_blue_bc[2]
      b = b * mired + self.p_blue_bc[1]
      b = b * mired + self.p_blue_bc[0]
    else:
      b = 0.

    return numpy.array([r, g, b], numpy.double)

def standalone(mired_to_rgb):
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

  rgb = mired_to_rgb.convert(mired)
  print(
    f'mired {mired:.3f} -> RGB ({rgb[RGB_RED]:.6f}, {rgb[RGB_GREEN]:.6f}, {rgb[RGB_BLUE]:.6f})'
  )
