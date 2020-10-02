#!/usr/bin/env python3

import math
import numpy
import sys

# old way (slower):
#from kelv_to_rgb_srgb import kelv_to_rgb_srgb

# new way (faster):
from mired_to_rgb_srgb import mired_to_rgb_srgb

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
  hue = hsbk[0]
  sat = hsbk[1]
  assert sat >= -EPSILON and sat < 1. + EPSILON
  br = hsbk[2]
  assert br >= -EPSILON and br < 1. + EPSILON
  kelv = hsbk[3]
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
  #kelv_rgb = kelv_to_rgb_srgb(kelv)

  # new way (faster):
  kelv_rgb = mired_to_rgb_srgb(1e6 / kelv)

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

  EXIT_FAILURE = 1

  if len(sys.argv) < 5:
    print(f'usage: {sys.argv[0]:s} hue sat br kelv')
    print('hue = hue in degrees (0 to 360)')
    print('sat = saturation as fraction (0 to 1)')
    print('br = brightness as fraction (0 to 1)')
    print('kelv = colour temperature in degrees Kelvin')
    sys.exit(EXIT_FAILURE)
  hsbk = numpy.array([float(i) for i in sys.argv[1:5]], numpy.double)

  rgb = hsbk_to_rgb(hsbk)
  print(
    f'HSBK ({hsbk[0]:.3f}, {hsbk[1]:.6f}, {hsbk[2]:.6f}, {hsbk[3]:.3f}) -> RGB ({rgb[0]:.6f}, {rgb[1]:.6f}, {rgb[2]:.6f})'
  )
