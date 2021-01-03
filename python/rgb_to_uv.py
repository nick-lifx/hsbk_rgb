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

RGB_RED = 0
RGB_GREEN = 1
RGB_BLUE = 2
N_RGB = 3

UVL_U = 0
UVL_V = 1
UVL_L = 2
N_UVL = 3

EPSILON = 1e-6

class RGBToUV:
  def __init__(self, gamma_decode, rgb_to_UVL):
    self.gamma_decode = gamma_decode
    self.rgb_to_UVL = rgb_to_UVL

  def convert(self, rgb):
    # validate inputs, allowing a little slack
    assert numpy.all(rgb >= -EPSILON) and numpy.all(rgb < 1. + EPSILON)
    assert numpy.sum(rgb) >= EPSILON

    UVL = self.rgb_to_UVL @ numpy.array(
      [self.gamma_decode(rgb[i]) for i in range(N_RGB)],
      numpy.double
    )
    return UVL[:UVL_L] / UVL[UVL_L]

def standalone(rgb_to_uv):
  import sys

  EXIT_SUCCESS = 0
  EXIT_FAILURE = 1

  UV_u = 0
  UV_v = 1
  N_UV = 2

  if len(sys.argv) < 4:
    print(f'usage: {sys.argv[0]:s} R G B')
    print('R = red channel as fraction (0 to 1)')
    print('G = green channel as fraction (0 to 1)')
    print('B = blue channel as fraction (0 to 1)')
    print('R, G and B cannot all be 0')
    sys.exit(EXIT_FAILURE)
  rgb = numpy.array([float(i) for i in sys.argv[1:4]], numpy.double)

  uv = rgb_to_uv.convert(rgb)
  print(
    f'RGB ({rgb[RGB_RED]:.6f}, {rgb[RGB_GREEN]:.6f}, {rgb[RGB_BLUE]:.6f}) -> uv ({uv[UV_u]:.6f}, {uv[UV_v]:.6f})'
  )
