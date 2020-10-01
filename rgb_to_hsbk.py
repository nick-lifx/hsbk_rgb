#!/usr/bin/env python3

import math
import numpy
import sys

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

# the following is a more accurate version of what would be printed by
#   ./hsbk_to_rgb.py 0 0 1 6504
# ideally it would be [1, 1, 1] but unfortunately D65 whitepoint != 6504K
kelv_rgb = numpy.array(
  # old way
  #[1.000000000000000, 0.974069550010795, 0.996829660858958],

  # new way (more efficient)
  [1.000000000000000, 0.976013921677787, 0.995894521802491],

  numpy.double
)

def rgb_to_hsbk(rgb):
  # validate inputs, allowing a little slack
  assert numpy.all(rgb >= -EPSILON) and numpy.all(rgb < 1. + EPSILON)

  # the Kelvin will always be 6504 with this simplified algorithm
  # we will set the other values if we are able to calculate them
  hsbk = numpy.array([0., 0., 0., 6504.], numpy.double)

  br = numpy.max(rgb)
  if br >= EPSILON:
    # it is not fully black, so we can calculate saturation
    # note: do not corrupt the caller's value by doing rgb /= br
    rgb = rgb / br

    # subtract as much of kelv_rgb as we are able to without going negative
    # this will result in at least one of R, G, B = 0 (i.e. a limiting one)
    kelv_factor = rgb / kelv_rgb
    i = numpy.argmin(kelv_factor)
    kelv_factor = kelv_factor[i]
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
      sat = hue_factor / (hue_factor + kelv_factor)

      # at this point hue_rgb[i] == 0 and hue_rgb[j] == 1 and i != j
      # using the (i, j) we can resolve the hue down to a 60 degree segment,
      # then rgb[k] such that k != i and k != j tells us where in the segment
      hue_base, hue_delta, k = hue_table[i][j]
      hue = hue_base + hue_delta * hue_rgb[k]

      hsbk[0] = hue
      hsbk[1] = sat

    hsbk[2] = br

  return hsbk

if __name__ == '__main__':
  import sys

  EXIT_FAILURE = 1

  if len(sys.argv) < 4:
    print(f'usage: {sys.argv[0]:s} R G B')
    print('R = red channel as fraction (0 to 1)')
    print('G = green channel as fraction (0 to 1)')
    print('B = blue channel as fraction (0 to 1)')
    sys.exit(EXIT_FAILURE)
  rgb = numpy.array([float(i) for i in sys.argv[1:4]], numpy.double)

  hsbk = rgb_to_hsbk(rgb)
  print(
    f'RGB ({rgb[0]:.6f}, {rgb[1]:.6f}, {rgb[2]:.6f}) -> HSBK ({hsbk[0]:.3f}, {hsbk[1]:.6f}, {hsbk[2]:.6f}, {hsbk[3]:.3f})'
  )
