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
N_HSBK = 4

HS_HUE = 0
HS_SAT = 1
N_HS = 2

BK_BR = 0
BK_KELV = 1
N_BK = 2

RGB_RED = 0
RGB_GREEN = 1
RGB_BLUE = 2
N_RGB = 3

RGBA_RED = 0
RGBA_GREEN = 1
RGBA_BLUE = 2
RGBA_ALPHA = 3
N_RGBA = 4

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
  def __init__(
    self,
    gamma_decode,
    gamma_encode,
    hsbk_to_rgb,
    wheel_size,
    dot_size,
    dot_rgb_mid = numpy.array([1., 1., 1.], numpy.double),
    dot_rgb_outer = numpy.array([0., 0., 0.], numpy.double)
  ):
    self.gamma_decode = gamma_decode
    self.gamma_encode = gamma_encode
    self.hsbk_to_rgb = hsbk_to_rgb

    # perform all calculations with pixel centres
    # a pixel will appear fully bright when its centre is inside the radius0
    # calculated here, therefore the radius will appear half a pixel larger;
    # alpha blending will operate when it is between the radius0 and radius1
    self.wheel_image_size = wheel_size * 2 + 1
    self.wheel_inner_radius = wheel_size * .5
    self.wheel_inner_radius0 = self.wheel_inner_radius - .5
    self.wheel_inner_radius1 = self.wheel_inner_radius + .5
    self.wheel_outer_radius = wheel_size
    self.wheel_outer_radius0 = self.wheel_outer_radius - .5
    self.wheel_outer_radius1 = self.wheel_outer_radius + .5

    self.dot_image_size = dot_size * 2 + 1
    self.dot_inner_radius = dot_size * .75
    self.dot_inner_radius0 = self.dot_inner_radius - .5
    self.dot_inner_radius1 = self.dot_inner_radius + .5
    self.dot_mid_radius = dot_size * .85
    self.dot_mid_radius0 = self.dot_mid_radius - .5
    self.dot_mid_radius1 = self.dot_mid_radius + .5
    self.dot_outer_radius = dot_size
    self.dot_outer_radius0 = self.dot_outer_radius - .5
    self.dot_outer_radius1 = self.dot_outer_radius + .5

    self.dot_rgb_mid = dot_rgb_mid
    self.dot_rgb_outer = dot_rgb_outer

  # this computes a linear blend in an SRGB image with correct gamma handling
  def blend(self, rgb0, rgb1, alpha):
    rgb = numpy.zeros((N_RGB,), numpy.double)
    for i in range(N_RGB):
      v0 = self.gamma_decode(rgb0[i])
      v1 = self.gamma_decode(rgb1[i])
      rgb[i] = self.gamma_encode(v0 + alpha * (v1 - v0))
    return rgb

  # this calls blend over an area, and implements PNG alpha semantics -- the
  # first (background) image must be RGB and the second (superimposed) image
  # must be RGBA, the x_off and y_off are relative to top left of background
  def composit(self, image0, image1, x_off, y_off):
    for i in range(image1.shape[0]):
      for j in range(image1.shape[1]):
        image0[i + y_off, j + x_off] = self.blend(
          image0[i + y_off, j + x_off],
          image1[i, j, :RGBA_ALPHA],
          image1[i, j, RGBA_ALPHA]
        )

  # finds hue and saturation corresponding to e.g. mouse position
  # also returns True if position is within circle or False if clipped
  # coordinates are relative to centre of top left pixel of wheel image
  def xy_to_hs(self, xy):
    x = xy[XY_x] - self.wheel_outer_radius0
    y = xy[XY_y] - self.wheel_outer_radius0
    rtheta = xy_to_rtheta(numpy.array([x, -y], numpy.double))
    r = rtheta[RTHETA_r]
    theta = rtheta[RTHETA_theta]

    hue = theta * 180. / math.pi
    sat = (
      (r - self.wheel_inner_radius) /
        (self.wheel_outer_radius - self.wheel_inner_radius)
    )
    within = True
    if sat < 0.:
      within = False
      sat = 0.
    elif sat > 1.:
      within = False
      sat = 1.
    sat = sat_decode(sat)
    return numpy.array([hue, sat], numpy.double), within

  # opposite of xy_to_hs(), except we know it must be within circle
  def hs_to_xy(self, hs):
    hue = hs[HS_HUE]
    sat = hs[HS_SAT]
    r = (
      sat_encode(sat) *
        (self.wheel_outer_radius - self.wheel_inner_radius) +
          self.wheel_inner_radius
    )
    theta = hue * math.pi / 180.

    return (
      rtheta_to_xy(numpy.array([r, -theta], numpy.double)) +
        numpy.array(
          [self.wheel_outer_radius0, self.wheel_outer_radius0],
          numpy.double
        )
    )

  # returns (size * 2 + 1, size * 2 + 1) by size sent to constructor
  # x_off and y_off are in the range [0, 1] and specify subpixel position
  # when both are 0 the image is left- and top-justified and will not use
  # right column or bottom row, similarly both 1 will not use top or left
  def render_wheel(self, bk, x_off = 0., y_off = 0.):
    br = bk[BK_BR]
    kelv = bk[BK_KELV]

    # coordinates are taken to be 0, 1, ..., size * 2
    # but we want to not use the last one (when x_off, y_off = 0) and take
    # the centre to be size - .5 and have radius size - .5 (as mentioned it
    # seem to be expanded by half a pixel on each side when actually viewed)
    x_off += self.wheel_outer_radius0
    y_off += self.wheel_outer_radius0

    image = numpy.zeros(
      (self.wheel_image_size, self.wheel_image_size, N_RGBA),
      numpy.double
    )
    for i in range(self.wheel_image_size):
      x = i - x_off
      for j in range(self.wheel_image_size):
        y = j - x_off

        rtheta = xy_to_rtheta(numpy.array([x, -y], numpy.double))
        r = rtheta[RTHETA_r]
        theta = rtheta[RTHETA_theta]

        if self.wheel_inner_radius0 <= r < self.wheel_outer_radius1:
          hue = theta * 180. / math.pi
          sat = (
            (r - self.wheel_inner_radius) /
              (self.wheel_outer_radius - self.wheel_inner_radius)
          )
          if sat < 0.:
            sat = 0.
          elif sat > 1.:
            sat = 1.
          sat = sat_decode(sat)
          image[j, i, :RGBA_ALPHA] = self.hsbk_to_rgb.convert(
            numpy.array([hue, sat, br, kelv], numpy.double)
          )
          image[j, i, RGBA_ALPHA] = (
            r - self.wheel_inner_radius0
          if r < self.wheel_inner_radius1 else
            1.
          if r < self.wheel_outer_radius0 else
            self.wheel_outer_radius1 - r
          )
    return image

  # returns (size * 2 + 1, size * 2 + 1) by size sent to constructor
  # x_off and y_off are in the range [0, 1] and specify subpixel position
  # when both are 0 the image is left- and top-justified and will not use
  # right column or bottom row, similarly both 1 will not use top or left
  def render_dot(self, hsbk, x_off = 0., y_off = 0.):
    # coordinates are taken to be 0, 1, ..., size * 2
    # but we want to not use the last one (when x_off, y_off = 0) and take
    # the centre to be size - .5 and have radius size - .5 (as mentioned it
    # seem to be expanded by half a pixel on each side when actually viewed)
    x_off += self.dot_outer_radius0
    y_off += self.dot_outer_radius0

    rgb_inner = self.hsbk_to_rgb.convert(hsbk)

    image = numpy.zeros(
      (self.dot_image_size, self.dot_image_size, N_RGBA),
      numpy.double
    )
    for i in range(self.dot_image_size):
      x = i - x_off
      for j in range(self.dot_image_size):
        y = j - y_off

        r = xy_to_r(numpy.array([x, y], numpy.double))

        if r < self.dot_outer_radius1:
          image[j, i, :RGBA_ALPHA] = (
            rgb_inner
          if r < self.dot_inner_radius0 else
            self.blend(
              rgb_inner,
              self.dot_rgb_mid,
              r - self.dot_inner_radius0
            )
          if r < self.dot_inner_radius1 else
            self.dot_rgb_mid
          if r < self.dot_mid_radius0 else
            self.blend(
              self.dot_rgb_mid,
              self.dot_rgb_outer,
              r - self.dot_mid_radius0
            )
          if r < self.dot_mid_radius1 else
            self.dot_rgb_outer
          )
          image[j, i, RGBA_ALPHA] = (
            1.
          if r < self.dot_outer_radius0 else
            self.dot_outer_radius1 - r
          )
    return image

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
    print(f'usage: {sys.argv[0]:s} [--device device] hue sat br kelv image_out')
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

  hue_wheel = HueWheel(gamma_decode, gamma_encode, hsbk_to_rgb, 120, 15)

  image = numpy.zeros((480, 272, 3), numpy.double)
  hue_wheel.composit(
    image,
    hue_wheel.render_wheel(hsbk[HSBK_BR:]),
    16,
    120
  )
  xy = hue_wheel.hs_to_xy(hsbk[:HSBK_BR])
  xy_frac, xy_int = numpy.modf(xy)
  hue_wheel.composit(
    image,
    hue_wheel.render_dot(hsbk, xy_frac[XY_x], xy_frac[XY_y]),
    16 - 15 + int(xy_int[XY_x]),
    120 - 15 + int(xy_int[XY_y])
  )

  imageio.imwrite(image_out, numpy.round(image * 255.).astype(numpy.uint8))
