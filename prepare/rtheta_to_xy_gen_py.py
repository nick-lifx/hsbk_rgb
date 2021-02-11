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

# put utils into path
# temporary until we have proper Python packaging
import os.path
import sys
dirname = os.path.dirname(__file__)
sys.path.append(os.path.join(dirname, '..'))

import math
import mpmath
import numpy
import utils.poly
import utils.yaml_io

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

mpmath.mp.prec = 106

#numpy.set_printoptions(threshold = numpy.inf)

if len(sys.argv) < 2:
  print(f'usage: {sys.argv[0]:s} rtheta_to_xy_fit_in.yml')
  sys.exit(EXIT_FAILURE)
rtheta_to_xy_fit_in = sys.argv[1]

rtheta_to_xy_fit = utils.yaml_io._import(
  utils.yaml_io.read_file(rtheta_to_xy_fit_in)
)
p = rtheta_to_xy_fit['p']
p_err = rtheta_to_xy_fit['p_err']
q = rtheta_to_xy_fit['q']
q_err = rtheta_to_xy_fit['q_err']

p = numpy.array(p, numpy.double)
q = numpy.array(q, numpy.double)

# rescale domain to compensate for range reduction code on entry
theta_scale = 2. / math.pi
r = numpy.array([0., 1. / theta_scale ** 2], numpy.double)
p = numpy.array(
  utils.poly.compose(mpmath.matrix(p), mpmath.matrix(r)),
  numpy.double
)
q = numpy.array(
  utils.poly.compose(mpmath.matrix(q), mpmath.matrix(r)),
  numpy.double
) / theta_scale

sys.stdout.write(
  sys.stdin.read().format(
    p_err = p_err,
    q_err = q_err,
    theta_scale = theta_scale,
    p_last = p[-1],
    p = ''.join(
      [
        '  x = x * theta2 {0:s} {1:.16e}\n'.format(
          '-' if p[i] < 0. else '+',
          abs(p[i])
        )
        for i in range(p.shape[0] - 2, -1, -1)
      ]
    ),
    q_last = q[-1],
    q = ''.join(
      [
        '  y = y * theta2 {0:s} {1:.16e}\n'.format(
          '-' if q[i] < 0. else '+',
          abs(q[i])
        )
        for i in range(q.shape[0] - 2, -1, -1)
      ]
    )
  )
)
