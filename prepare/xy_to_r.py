#!/usr/bin/env python3

import math
import numpy

XY_x = 0
XY_y = 1
N_XY = 2

alpha_beta = numpy.array(
  [
    # a: 0.0 b: 0.25 err: 7.070034951484061e-06
    [0.9962467349583078, 0.12264357565415689],

    # a: 0.25 b: 0.5 err: 4.483456904624816e-06
    [0.9406977021298616, 0.3479867264055142],

    # a: 0.5 b: 1 err: 2.1114131347532705e-05
    [0.8165310585258534, 0.5885222903731413],

    # a: 1 b: 2 err: 2.1114131347532705e-05
    [0.5885222903731413, 0.8165310585258534],

    # a: 2 b: 4 err: 4.483456904624816e-06
    [0.3479867264055142, 0.9406977021298616],

    # a: 4 b: inf err: 7.070034951484061e-06
    [0.12264357565415689, 0.9962467349583078]
  ],
  numpy.double
)

def xy_to_r(xy):
  abs_xy = numpy.abs(xy)
  abs_x = abs_xy[XY_x]
  abs_y = abs_xy[XY_y]
  r = abs_xy @ alpha_beta[
    sum([abs_y >= math.ldexp(abs_x, i) for i in range(-2, 3)]),
    :
  ]
  return .5 * (r + numpy.sum(numpy.square(xy)) / r)

for i in range(360):
  theta = i * math.pi / 180.
  r = xy_to_r(numpy.array([math.cos(theta), math.sin(theta)], numpy.double))
  print('i', i, 'tan', math.tan(theta), 'err', r - 1.)
