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

RGB_RED = 0
RGB_GREEN = 1
RGB_BLUE = 2
N_RGB = 3

HSBK_HUE = 0
HSBK_SAT = 1
HSBK_BR = 2
HSBK_KELV = 3
N_HSBK = 4

EPSILON = 1e-6

# table for looking up hues when rgb[i] == 0 and rgb[j] == 1
hue_table = [
  # no red (cyans)
  {
    1: (120.,  60., 2), # i = 0, j = 1 (more green): hue = 120 + 60 * rgb[2]
    2: (240., -60., 1)  # i = 0, j = 2 (more blue): hue = 240 - 60 * rgb[1]
  },
  # no green (magentas)
  {
    0: (360., -60., 2), # i = 1, j = 0 (more red): hue = 360 - 60 * rgb[2]
    2: (240.,  60., 0)  # i = 1, j = 2 (more blue): hue = 240 + 60 * rgb[0]
  },
  # no blue (yellows)
  {
    0: (  0.,  60., 1),  # i = 2, j = 0 (more red): hue = 0 + 60 * rgb[1]
    1: (120., -60., 0)   # i = 2, j = 1 (more green): hue = 120 - 60 * rgb[0]
  }
]

def rgb_to_hsbk(kelv_rgb_6504K, mired_to_rgb, rgb, kelv = None):
  # validate inputs, allowing a little slack
  assert numpy.all(rgb >= -EPSILON) and numpy.all(rgb < 1. + EPSILON)

  hsbk = numpy.array([0., 0., 0., 0.], numpy.double)
  if kelv is None:
    hsbk[HSBK_KELV] = 6504.
    kelv_rgb = kelv_rgb_6504K
  else:
    hsbk[HSBK_KELV] = kelv
    kelv_rgb = mired_to_rgb.convert(1e6 / kelv)

  br = numpy.max(rgb)
  if br >= EPSILON:
    # it is not fully black, so we can calculate saturation
    # note: do not corrupt the caller's value by doing rgb /= br
    hsbk[HSBK_BR] = br
    rgb = rgb / br

    # subtract as much of kelv_rgb as we are able to without going negative
    # this will result in at least one of R, G, B = 0 (i.e. a limiting one)
    # we rely on the fact that kelv_rgb[RGB_RED] cannot go below about .7
    kelv_factor = rgb[RGB_RED] / kelv_rgb[RGB_RED]
    i = RGB_RED
    if rgb[RGB_GREEN] < kelv_factor * kelv_rgb[RGB_GREEN]:
      kelv_factor = rgb[RGB_GREEN] / kelv_rgb[RGB_GREEN]
      i = RGB_GREEN
    if rgb[RGB_BLUE] < kelv_factor * kelv_rgb[RGB_BLUE]:
      kelv_factor = rgb[RGB_BLUE] / kelv_rgb[RGB_BLUE]
      i = RGB_BLUE
    hue_rgb = rgb - kelv_factor * kelv_rgb
    assert hue_rgb[i] < EPSILON

    # at this point we can regenerate the original rgb by
    #   rgb = hue_rgb + kelv_factor * kelv_rgb
    # we will now scale up hue_rgb so that at least one of R, G, B = 1,
    # and record hue_factor to scale it down again to maintain the above
    j = numpy.argmax(hue_rgb)
    hue_factor = hue_rgb[j]
    if hue_factor >= EPSILON:
      # it is not fully white, so we can calculate hue
      assert j != i # we know hue_rgb[i] < EPSILON, hue_rgb[j] >= EPSILON
      hue_rgb /= hue_factor

      # at this point we can regenerate the original rgb by
      #   rgb = hue_factor * hue_rgb + kelv_factor * kelv_rgb
      # if we now re-scale it so that hue_factor + kelv_factor == 1, then
      # hue_factor will be the saturation (sum will be approximately 1, it may
      # be larger, if hue_rgb and kelv_rgb are either side of the white point)
      hsbk[HSBK_SAT] = hue_factor / (hue_factor + kelv_factor)

      # at this point hue_rgb[i] == 0 and hue_rgb[j] == 1 and i != j
      # using the (i, j) we can resolve the hue down to a 60 degree segment,
      # then rgb[k] such that k != i and k != j tells us where in the segment
      hue_base, hue_delta, channel = hue_table[i][j]
      hsbk[HSBK_HUE] = hue_base + hue_delta * hue_rgb[channel]

  return hsbk

def standalone(_rgb_to_hsbk):
  import sys

  EXIT_SUCCESS = 0
  EXIT_FAILURE = 1

  RGB_RED = 0
  RGB_GREEN = 1
  RGB_BLUE = 2
  N_RGB = 3

  if len(sys.argv) < 4:
    print(f'usage: {sys.argv[0]:s} R G B [kelv]')
    print('R = red channel as fraction (0 to 1)')
    print('G = green channel as fraction (0 to 1)')
    print('B = blue channel as fraction (0 to 1)')
    print('kelv = white point to use in conversion (in degrees Kelvin; default 6504K)')
    sys.exit(EXIT_FAILURE)
  rgb = numpy.array([float(i) for i in sys.argv[1:4]], numpy.double)
  kelv = float(sys.argv[4]) if len(sys.argv) >= 5 else None

  hsbk = _rgb_to_hsbk(rgb, kelv)
  print(
    f'RGB ({rgb[RGB_RED]:.6f}, {rgb[RGB_GREEN]:.6f}, {rgb[RGB_BLUE]:.6f}) -> HSBK ({hsbk[HSBK_HUE]:.3f}, {hsbk[HSBK_SAT]:.6f}, {hsbk[HSBK_BR]:.6f}, {hsbk[HSBK_KELV]:.3f})'
  )
