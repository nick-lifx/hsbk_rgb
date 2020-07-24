#!/usr/bin/env python3

import numpy

# these contain the published (x, y) rgbw_to_xy of the SRGB system
# see https://en.wikipedia.org/wiki/SRGB
# across is R, G, B, W and down is x, y
# the last one is not actually a primary but the so-called white point
# this means that R + G + B all at full intensity should make the given (x, y)
rgbw_to_xy = numpy.array(
  [
    [0.6400, 0.3000, 0.1500, 0.3127],
    [0.3300, 0.6000, 0.0600, 0.3290]
  ],
  numpy.double
)

# add the missing z row, to convert the primaries from (x, y) to (X, Y, Z)
# see https://en.wikipedia.org/wiki/CIE_1931_color_space#CIE_xy_chromaticity_diagram_and_the_CIE_xyY_color_space
x = rgbw_to_xy[0, :]
y = rgbw_to_xy[1, :]
rgbw_to_XYZ = numpy.stack([x, y, 1. - x - y], 0)

# find the linear combination of R, G, B rgbw_to_xy to make the white point
x = numpy.linalg.solve(rgbw_to_XYZ[:, :3], rgbw_to_XYZ[:, 3])

# then scale R, G, B by those factors so the primaries sum to the white point
# at this point the white point is not needed any more, so trim it off
rgb_to_XYZ = rgbw_to_XYZ[:, :3] * x[numpy.newaxis, :]

# and finally convert from the (X, Y, Z) system to the (U, V, W) system
# see https://en.wikipedia.org/wiki/CIE_1960_color_space
XYZ_to_UVW = numpy.array(
  [
    [2. / 3., 0., 0.],
    [0., 1., 0.],
    [-1. / 2., 3. / 2, 1. / 2.]
  ],
  numpy.double
)
rgb_to_UVW = XYZ_to_UVW @ rgb_to_XYZ

# we want to convert Kelvin -> (u, v) -> (U, V, W) -> (R, G, B)
# to make this as easy as possible we invert the above-calculated matrix
UVW_to_rgb = numpy.linalg.inv(rgb_to_UVW)

# print it out as Python code that can be inserted into hsbk_to_rgb.py
print(
  f'''UVW_to_rgb = numpy.array(
  [
    [{UVW_to_rgb[0, 0]:.8f}, {UVW_to_rgb[0, 1]:.8f}, {UVW_to_rgb[0, 2]:.8f}],
    [{UVW_to_rgb[1, 0]:.8f}, {UVW_to_rgb[1, 1]:.8f}, {UVW_to_rgb[1, 2]:.8f}],
    [{UVW_to_rgb[2, 0]:.8f}, {UVW_to_rgb[2, 1]:.8f}, {UVW_to_rgb[2, 2]:.8f}]
  ],
  numpy.double
)'''
)
