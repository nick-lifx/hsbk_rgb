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

import numpy
import math
import poly
import remez
import ruamel.yaml
import scipy.optimize
import sys
from numpy_to_python import numpy_to_python
from python_to_numpy import python_to_numpy

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

ORDER = 2
NEWTON_ITERS = 1
ERR_ORDER = 24

EPSILON = 1e-12

diag = False
if len(sys.argv) >= 2 and sys.argv[1] == '--diag':
  diag = True
  del sys.argv[1]
if len(sys.argv) < 2:
  print(f'usage: {sys.argv[0]} alpha_max_beta_min_fit_out.yml')
  sys.exit(EXIT_FAILURE)
alpha_max_beta_min_fit_out = sys.argv[1]

yaml = ruamel.yaml.YAML(typ = 'safe')
#numpy.set_printoptions(threshold = numpy.inf)

# function to be approximated
def f(x):
  return numpy.sqrt(x ** 2 + 1.)
a = 0.
b = 1.

# find approximating polynomial
p, x, err = remez.remez(f, a, b, ORDER, ERR_ORDER)
err = err ** 2

def g(p, x):
  y1 = f(x)
  y2 = y1 ** 2
  y = poly.eval(p, x)
  for i in range(NEWTON_ITERS):
    y = .5 * (y + y2 / y)
  return y / y1 - 1.

#x_mid = numpy.array(
#  [
#    scipy.optimize.minimize_scalar(
#      lambda x: g(p, x),
#      bounds = x[i:i + 2],
#      method = 'Bounded',
#      options = {'disp': True, 'xatol': EPSILON}
#    ).x
#    for i in range(ORDER)
#  ],
#  numpy.double
#)
#print('x_mid', x_mid, 'g(p, x_mid)', g(p, x_mid))

for i in range(10):
  print('i', i)

  p = scipy.optimize.minimize(
    lambda p_err: numpy.sum(
      numpy.square(
        numpy.concatenate(
          [
            g(p_err[:-1], x) - p_err[-1] #,
            #g(p_err[:-1], x_mid)
          ],
          0
        )
      )
    ),
    numpy.array(list(p) + [err], numpy.double),
    method = 'Nelder-Mead',
    options = {'disp': True, 'xatol': EPSILON}
  ).x[:-1]
  print('p', p, 'g(p, x)', g(p, x))

  #x0 = numpy.linspace(a, b, 1000, numpy.double)
  #import matplotlib.pyplot
  #matplotlib.pyplot.plot(x0, f(x0))
  #matplotlib.pyplot.plot(x0, poly.eval(p, x0))
  #matplotlib.pyplot.show()

  x_mid = numpy.array(
    [
      scipy.optimize.minimize_scalar(
        lambda x: g(p, x),
        bounds = x[i:i + 2],
        method = 'Bounded',
        options = {'disp': True, 'xatol': EPSILON}
      ).x
      for i in range(ORDER)
    ],
    numpy.double
  )
  print('x_mid', x_mid, 'g(p, x_mid)', g(p, x_mid))

  xb = numpy.array([a] + list(x_mid) + [b], numpy.double)
  x = numpy.array(
    [
      scipy.optimize.minimize_scalar(
        lambda x: -g(p, x),
        bounds = xb[i:i + 2],
        method = 'Bounded',
        options = {'disp': True, 'xatol': EPSILON}
      ).x
      for i in range(ORDER + 1)
    ],
    numpy.double
  )
  print('x', x, 'g(p, x)', g(p, x))
  err = numpy.max(g(p, x))

# checking
if diag:
  import matplotlib.pyplot

  x = numpy.linspace(a, b, 1000, numpy.double)
  matplotlib.pyplot.plot(x, f(x))
  matplotlib.pyplot.plot(x, f(x) * (g(p, x) + 1.))

  matplotlib.pyplot.show()

alpha_max_beta_min_fit = {
  'a': a,
  'b': b,
  'p': p,
  'err': float(err),
  'newton_iters': NEWTON_ITERS
}
with open(alpha_max_beta_min_fit_out, 'w') as fout:
  yaml.dump(numpy_to_python(alpha_max_beta_min_fit), fout)
