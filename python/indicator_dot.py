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
from xy_to_r import xy_to_r

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

RGB_RED = 0
RGB_GREEN = 1
RGB_BLUE = 2
N_RGB = 3

RGBA_RED = 0
RGBA_GREEN = 1
RGBA_BLUE = 2
RGBA_ALPHA = 3
N_RGBA = 4

XY_x = 0
XY_y = 1
N_XY = 2

EPSILON = 1e-6

class IndicatorDot:
  def __init__(
    self,
    gamma_decode,
    gamma_encode,
    dot_size,
    dot_rgb_mid = numpy.array([1., 1., 1.], numpy.double),
    dot_rgb_outer = numpy.array([0., 0., 0.], numpy.double)
  ):
    self.gamma_decode = gamma_decode
    self.gamma_encode = gamma_encode

    self.dot_size = dot_size
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
  # must be RGBA, the x_off, y_off are relative to bottom left of background
  def composit(self, image0, image1, x_off, y_off):
    for i in range(image1.shape[0]):
      for j in range(image1.shape[1]):
        image0[i + y_off, j + x_off] = self.blend(
          image0[i + y_off, j + x_off],
          image1[i, j, :RGBA_ALPHA],
          image1[i, j, RGBA_ALPHA]
        )

  # returns (size * 2 + 1, size * 2 + 1) by size sent to constructor
  # x_off and y_off are in the range [0, 1] and specify subpixel position
  # when both are 0 the image is left-, bottom -justified and will not use
  # right column or top row, similarly both 1 will not use bottom or right
  def render_dot(self, rgb_inner, x_off = 0., y_off = 0.):
    # coordinates are taken to be 0, 1, ..., size * 2
    # but we want to not use the last one (when x_off, y_off = 0) and take
    # the centre to be size - .5 and have radius size - .5 (as mentioned it
    # seem to be expanded by half a pixel on each side when actually viewed)
    x_off += self.dot_size
    y_off += self.dot_size

    xy = numpy.zeros((N_XY,), numpy.double)

    image = numpy.zeros(
      (self.dot_image_size, self.dot_image_size, N_RGBA),
      numpy.double
    )
    for i in range(self.dot_image_size):
      xy[XY_y] = i + .5 - y_off
      for j in range(self.dot_image_size):
        xy[XY_x] = j + .5 - x_off
        r = xy_to_r(xy)
        if r < self.dot_outer_radius1:
          image[i, j, :RGBA_ALPHA] = (
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
          image[i, j, RGBA_ALPHA] = (
            1.
          if r < self.dot_outer_radius0 else
            self.dot_outer_radius1 - r
          )
    return image
