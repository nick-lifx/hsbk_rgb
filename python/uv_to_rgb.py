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

class UVToRGB:
  def __init__(self, UVL_to_rgb, gamma_encode):
    self.UVL_to_rgb = UVL_to_rgb
    self.gamma_encode = gamma_encode

  def convert(self, uv):
    # validate inputs, allowing a little slack
    assert numpy.all(uv >= -EPSILON) and numpy.sum(uv) < 1. + EPSILON

    # convert (u, v) to (R, G, B) in an optimized way
    # usually we would calculate w such that u + v + w = 1 and then take
    # (u, v, w) as (U, V, W) noting that brightness is arbitrary, and then
    # multiply through by a UVW -> rgb conversion matrix, but the matrix
    # used here expects L = U + V + W instead of W and L is always 1 here
    rgb = self.UVL_to_rgb[:, UVL_L] + self.UVL_to_rgb[:, :UVL_L] @ uv

    # low Kelvins are outside the gamut of SRGB and thus must be interpreted,
    # in this simplistic approach we simply clip off the negative blue value
    rgb[rgb < 0.] = 0.

    # normalize the brightness, so that at least one of R, G, or B = 1
    rgb /= numpy.max(rgb)

    # return gamma-encoded (R, G, B) tuple according to the SRGB gamma curve
    # because displaying it on a monitor will gamma-decode it in the process
    return numpy.array(
      [self.gamma_encode(rgb[i]) for i in range(N_RGB)],
      numpy.double
    )

def standalone(uv_to_rgb):
  import sys

  EXIT_SUCCESS = 0
  EXIT_FAILURE = 1

  UV_u = 0
  UV_v = 1
  N_UV = 2

  if len(sys.argv) < 3:
    print(f'usage: {sys.argv[0]:s} u v')
    print('u = CIE 1960 u coordinate (0 to 1)')
    print('v = CIE 1960 v coordinate (0 to 1)')
    print('sum of u and v cannot exceed 1')
    sys.exit(EXIT_FAILURE)
  uv = numpy.array([float(i) for i in sys.argv[1:3]], numpy.double)

  rgb = uv_to_rgb.convert(uv)
  print(
    f'uv ({uv[UV_u]:.6f}, {uv[UV_v]:.6f}) -> RGB ({rgb[RGB_RED]:.6f}, {rgb[RGB_GREEN]:.6f}, {rgb[RGB_BLUE]:.6f})'
  )
