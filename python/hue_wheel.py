#!/usr/bin/env python3

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
from rtheta_to_xy import rtheta_to_xy
from xy_to_r import xy_to_r
from xy_to_rtheta import xy_to_rtheta

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

HSBK_HUE = 0
HSBK_SAT = 1
HSBK_BR = 2
HSBK_KELV = 3

RGB_RED = 0
RGB_GREEN = 1
RGB_BLUE = 2
N_RGB = 3

RTHETA_r = 0
RTHETA_theta = 1
N_RTHETA = 2

XY_x = 0
XY_y = 1
N_XY = 2

EPSILON = 1e-6

# these functions present a slightly modified saturation scale to user,
# giving more space to the whites (behaves like gamma but faster to compute)
SAT_DECODE_GAMMA = 1.1
SAT_ENCODE_GAMMA = 1. / SAT_DECODE_GAMMA
def sat_decode(x):
  return x / ((1. - SAT_DECODE_GAMMA) * x + SAT_DECODE_GAMMA)
def sat_encode(x):
  return x / ((1. - SAT_ENCODE_GAMMA) * x + SAT_ENCODE_GAMMA)

class HueWheel:
  def __init__(self, gamma_decode, gamma_encode, hsbk_to_rgb):
    self.gamma_decode = gamma_decode
    self.gamma_encode = gamma_encode
    self.hsbk_to_rgb = hsbk_to_rgb

  # this computes a linear blend in an SRGB image with correct gamma handling
  def blend(self, rgb0, rgb1, alpha):
    rgb = numpy.zeros((N_RGB,), numpy.double)
    for i in range(N_RGB):
      v0 = self.gamma_decode(rgb0[i])
      v1 = self.gamma_decode(rgb1[i])
      rgb[i] = self.gamma_encode(v0 + alpha * (v1 - v0))
    return rgb

  def render_wheel(self, br, kelv, image):
    for i in range(240):
      print(i, '/', 240)
      x = i - 119.5
      for j in range(240):
        y = j - 119.5
  
        rtheta = xy_to_rtheta(numpy.array([x, -y], numpy.double))
        r = rtheta[RTHETA_r]
        theta = rtheta[RTHETA_theta]
  
        if 60. <= r < 120.:
          hue = theta * 180. / math.pi
          sat = sat_decode((r - 60.) / 60.)
          rgb = hsbk_to_rgb.convert(
            numpy.array([hue, sat, br, kelv], numpy.double)
          )
          image[120 + j, 16 + i, :] = (
            self.blend(
              image[120 + j, 16 + i],
              rgb,
              r - 60.
            )
          if r < 61. else
            rgb
          if r < 119. else
             self.blend(
              rgb,
              image[120 + j, 16 + i],
              r - 119.
            )
          )

  def render_dot(self, hsbk, image):
    hue = hsbk[HSBK_HUE]
    sat = hsbk[HSBK_SAT]

    rgb_inner = hsbk_to_rgb.convert(hsbk)
    rgb_outer = numpy.array([1., 1., 1.], numpy.double)
    rgb_outline = numpy.array([0., 0., 0.], numpy.double)
  
    r = sat_encode(sat) * 60. + 60.
    theta = hue * math.pi / 180.
    xy = (
      rtheta_to_xy(numpy.array([r, -theta], numpy.double)) +
        numpy.array([136., 240.], numpy.double)
    )
    xy_frac, xy_int = numpy.modf(xy)
    xy_int = xy_int.astype(numpy.int32) - numpy.array([15, 15], numpy.int32)
    for i in range(31):
      x = i - 14.5 - xy_frac[XY_x]
      for j in range(31):
        y = j - 14.5 - xy_frac[XY_y]
  
        r = xy_to_r(numpy.array([x, y], numpy.double))
  
        if r < 15.:
          image[xy_int[XY_y] + j, xy_int[XY_x] + i, :] = (
            rgb_inner
          if r < 10. else
            self.blend(rgb_inner, rgb_outer, r - 10.)
          if r < 11. else
            rgb_outer
          if r < 12.5 else
            self.blend(rgb_outer, rgb_outline, r - 12.5)
          if r < 13.5 else
            rgb_outline
          if r < 14. else
            self.blend(
              rgb_outline,
              image[xy_int[XY_y] + j, xy_int[XY_x] + i, :],
              r - 14.
            )
          )

if __name__ == '__main__':
  import imageio
  from gamma_decode_rec2020 import gamma_decode_rec2020
  from gamma_decode_srgb import gamma_decode_srgb
  from gamma_encode_rec2020 import gamma_encode_rec2020
  from gamma_encode_srgb import gamma_encode_srgb
  from hsbk_to_rgb_display_p3 import hsbk_to_rgb_display_p3
  from hsbk_to_rgb_rec2020 import hsbk_to_rgb_rec2020
  from hsbk_to_rgb_srgb import hsbk_to_rgb_srgb

  device = 'srgb'
  if len(sys.argv) >= 3 and sys.argv[1] == '--device':
    device = sys.argv[2]
    del sys.argv[1:3]
  if len(sys.argv) < 6:
    print(f'usage: {sys.argv[0]:s} [--device device] [hue sat br kelv image_out]')
    print('device in {display_p3, rec2020, srgb}, default srgb')
    print('hue = hue in degrees (0 to 360)')
    print('sat = saturation as fraction (0 to 1)')
    print('br = brightness as fraction (0 to 1)')
    print('kelv = white point in degrees Kelvin')
    print('image_out = name of PNG file to create (will be overwritten)')
    print('creates 272 x 480 x 3 image with colour wheel and indicator circle')
    sys.exit(EXIT_FAILURE)
  hsbk = numpy.array(
    [
      float(sys.argv[1]),
      float(sys.argv[2]),
      float(sys.argv[3]),
      float(sys.argv[4])
    ],
    numpy.double
  )
  image_out = sys.argv[5]

  gamma_decode, gamma_encode, hsbk_to_rgb = {
    'display_p3': (
      gamma_decode_srgb,
      gamma_encode_srgb,
      hsbk_to_rgb_display_p3
    ),
    'rec2020': (
      gamma_decode_rec2020,
      gamma_encode_rec2020,
      hsbk_to_rgb_rec2020
    ),
    'srgb': (
      gamma_decode_srgb,
      gamma_encode_srgb,
      hsbk_to_rgb_srgb
    )
  }[device]

  hue_wheel = HueWheel(gamma_decode, gamma_encode, hsbk_to_rgb)

  image = numpy.zeros((480, 272, 3), numpy.double)
  hue_wheel.render_wheel(hsbk[HSBK_BR], hsbk[HSBK_KELV], image)
  hue_wheel.render_dot(hsbk, image)

  imageio.imwrite(image_out, numpy.round(image * 255.).astype(numpy.uint8))
