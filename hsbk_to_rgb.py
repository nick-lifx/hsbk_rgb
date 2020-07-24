#!/usr/bin/env python3

import math
import numpy
import sys
from kelv_to_uv import kelv_to_uv

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

# this allows us to convert chromaticity to RGB, in the SRGB system
# see primaries.py in this repository for how this matrix is calculated
UVW_to_rgb = numpy.array(
  [
    [12.50315736, -0.12629452, -3.03106845],
    [-4.22958319, 5.32310738, 0.25261433],
    [5.07265164, -10.25802888, 6.42535875]
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

  # find the approximate (u, v) chromaticity of the given Kelvin value
  uv = kelv_to_uv(kelv)

  # add the missing w, to convert the chromaticity from (u, v) to (U, V, W)
  # see https://en.wikipedia.org/wiki/CIE_1960_color_space
  u = uv[0]
  v = uv[1]
  UVW = numpy.array([u, v, 1. - u - v], numpy.double)

  # convert to rgb in the SRGB system (the brightness will be arbitrary)
  kelv_rgb = UVW_to_rgb @ UVW

  # low Kelvins are outside the gamut of SRGB and thus must be interpreted,
  # in this simplistic approach we simply clip off the negative blue value
  kelv_rgb[kelv_rgb < 0.] = 0.

  # normalize the brightness, so that at least one of R, G, or B = 1
  kelv_rgb /= numpy.max(kelv_rgb)

  # gamma-encode the R, G, B tuple according to the SRGB gamma curve
  # because displaying it on a monitor will gamma-decode it in the process
  mask = kelv_rgb < .0031308
  kelv_rgb[mask] *= 12.92
  kelv_rgb[~mask] = 1.055 * kelv_rgb[~mask] ** (1. / 2.4) - 0.055

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
  # user is supposed to pass 0..1 values, we will allow a little slack
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
