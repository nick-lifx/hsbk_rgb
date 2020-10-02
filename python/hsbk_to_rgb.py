#!/usr/bin/env python3

import math
import numpy
import sys

# old way (slower):
#from kelv_to_rgb import kelv_to_rgb

# new way (faster):
from mired_to_rgb import mired_to_rgb

HSBK_HUE = 0
HSBK_SAT = 1
HSBK_BR = 2
HSBK_KELV = 3
N_HSBK = 4

# define hues as red->yellow->green->cyan->blue->magenta->red again
# across is hue 0, 60, 120, 180, 240, 300, 360, down is R, G, B
# for interpolation, e.g. hue of 10 = column 1 + 10/60 * (column 2 - column 1)
hue_sequence = numpy.array(
  [
    [1., 1., 0., 0., 0., 1., 1.],
    [0., 1., 1., 1., 0., 0., 0.],
    [0., 0., 0., 1., 1., 1., 0.]
  ],
  numpy.double
)

EPSILON = 1e-6

def hsbk_to_rgb(hsbk):
  # validate inputs, allowing a little slack
  # the hue does not matter as it will be normalized modulo 360
  hue = hsbk[HSBK_HUE]
  sat = hsbk[HSBK_SAT]
  assert sat >= -EPSILON and sat < 1. + EPSILON
  br = hsbk[HSBK_BR]
  assert br >= -EPSILON and br < 1. + EPSILON
  kelv = hsbk[HSBK_KELV]
  assert kelv >= 1500. - EPSILON and kelv < 9000. + EPSILON

  # this section computes hue_rgb from hue

  # put it in the form hue = (i + j) * 60 where i is integer, j is fraction
  hue /= 60.
  i = math.floor(hue)
  j = hue - i
  i %= 6

  # interpolate from the table
  # interpolation is done in gamma-encoded space, as Photoshop HSV does it
  # the result of this interpolation will have at least one of R, G, B = 1
  hue_rgb = (
    hue_sequence[:, i] +
      j * (hue_sequence[:, i + 1] - hue_sequence[:, i])
  )

  # this section computes kelv_rgb from kelv

  # old way (slower):
  #kelv_rgb = kelv_to_rgb(kelv)

  # new way (faster):
  kelv_rgb = mired_to_rgb(1e6 / kelv)

  # this section applies the saturation

  # do the mixing in gamma-encoded RGB space
  # this is not very principled and can corrupt the chromaticities
  rgb = kelv_rgb + sat * (hue_rgb - kelv_rgb)

  # normalize the brightness again
  # this is needed because SRGB produces the brightest colours near the white
  # point, so if hue_rgb and kelv_rgb are on opposite sides of the white point,
  # then rgb could land near the white point, but not be as bright as possible
  rgb /= numpy.max(rgb)

  # this section applies the brightness

  # do the scaling in gamma-encoded RGB space
  # this is not very principled and can corrupt the chromaticities
  rgb *= br

  return rgb

if __name__ == '__main__':
  import sys

  EXIT_SUCCESS = 0
  EXIT_FAILURE = 1

  RGB_RED = 0
  RGB_GREEN = 1
  RGB_BLUE = 2
  N_RGB = 3

  if len(sys.argv) < 4:
    print(f'usage: {sys.argv[0]:s} hue sat br [kelv]')
    print('hue = hue in degrees (0 to 360)')
    print('sat = saturation as fraction (0 to 1)')
    print('br = brightness as fraction (0 to 1)')
    print('kelv = white point in degrees Kelvin (defaults to 6504K)')
    sys.exit(EXIT_FAILURE)
  hsbk = numpy.array(
    [
      float(sys.argv[1]),
      float(sys.argv[2]),
      float(sys.argv[3]),
      float(sys.argv[4]) if len(sys.argv) >= 5 else 6504.
    ],
    numpy.double
  )

  rgb = hsbk_to_rgb(hsbk)
  print(
    f'HSBK ({hsbk[HSBK_HUE]:.3f}, {hsbk[HSBK_SAT]:.6f}, {hsbk[HSBK_BR]:.6f}, {hsbk[HSBK_KELV]:.3f}) -> RGB ({rgb[RGB_RED]:.6f}, {rgb[RGB_GREEN]:.6f}, {rgb[RGB_BLUE]:.6f})'
  )
