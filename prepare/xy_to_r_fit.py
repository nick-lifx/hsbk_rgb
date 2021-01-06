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

import numpy
import numpy.linalg
import math
import mpmath
import scipy.optimize
import utils.poly
import utils.poly_fit
import utils.remez
import utils.yaml_io

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

ORDER = 8
EPSILON = 1e-9
NEWTON_ITERS = 1

mpmath.mp.prec = 106

#numpy.set_printoptions(threshold = numpy.inf)

diag = False
if len(sys.argv) >= 2 and sys.argv[1] == '--diag':
  diag = True
  del sys.argv[1]
if len(sys.argv) < 2:
  print(f'usage: {sys.argv[0]} xy_to_r_fit_out.yml')
  sys.exit(EXIT_FAILURE)
xy_to_r_fit_out = sys.argv[1]

breaks = numpy.array([0., .25, .5, 1.], numpy.double)

a = math.atan(breaks[0])
b = math.atan(breaks[-1])
p_cos = utils.poly_fit.any_f_to_poly(
  lambda theta: mpmath.matrix(
    [mpmath.cos(theta[i]) for i in range(theta.rows)]
  ),
  a,
  b,
  ORDER
)
p_sin = utils.poly_fit.any_f_to_poly(
  lambda theta: mpmath.matrix(
    [mpmath.sin(theta[i]) for i in range(theta.rows)]
  ),
  a,
  b,
  ORDER
)

p = []
err = []
for i in range(breaks.shape[0] - 1):
  a = math.atan(breaks[i])
  b = math.atan(breaks[i + 1])

  # objective to minimize
  def f(x):
    # evaluate error of the given alpha-max-beta-min formula,
    # for max = cos(theta), min = sin(theta), a <= theta <= b
    alpha = mpmath.mpf(x[0])
    beta = mpmath.mpf(x[1])
    p_alpha_cos_beta_sin = alpha * p_cos + beta * p_sin
    def g(theta):
      # calculate output of alpha-max-beta-min for each theta-value
      y = utils.poly.eval_multi(
        p_alpha_cos_beta_sin,
        mpmath.matrix(theta)
      )

      # optionally apply some iterations of Newton-Raphson square root
      # this means the alpha, beta will be optimized to return the best
      # error AFTER the Newton-Raphson has been applied at run-time
      for i in range(NEWTON_ITERS):
        y = mpmath.matrix(
          [
            .5 * (y[j] + 1. / y[j])
            for j in range(y.rows)
          ]
        )

      return y - 1.
    _, y = utils.poly.extrema(
      utils.poly_fit.any_f_to_poly(g, a, b, ORDER),
      a,
      b
    )
    return float(max([abs(y[i]) for i in range(y.rows)]))

  # initial estimate, fit to endpoints and midpoint
  c = .5 * (a + b)
  x0, _, _, _ = numpy.linalg.lstsq(
    numpy.array(
      [
        [math.cos(a), math.sin(a)],
        [math.cos(b), math.sin(b)],
        [math.cos(c), math.sin(c)]
      ],
      numpy.double
    ),
    numpy.array([1., 1., 1.], numpy.double),
    rcond = None
  )
  z0 = f(x0)
  print('x0', x0, 'z0', z0)

  x = scipy.optimize.minimize(
    f,
    x0,
    method = 'Nelder-Mead',
    options = {'disp': True, 'xatol': EPSILON}
  ).x
  z = f(x)
  print('x', x, 'z', z)

  p.append(x)
  err.append(z)
p = numpy.stack(p, 0)
err = numpy.array(err, numpy.double)

utils.yaml_io.write_file(
  xy_to_r_fit_out,
  utils.yaml_io.export(
    {
      'breaks': breaks,
      'p': p,
      'err': err
    }
  )
)
