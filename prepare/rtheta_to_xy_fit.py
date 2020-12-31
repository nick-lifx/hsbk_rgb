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
import math
import mpmath
import utils.remez
import utils.yaml_io

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

ORDER1 = 4
ORDER2 = 3
ERR_ORDER = 16
EPSILON = 1e-4

mpmath.mp.prec = 212

#numpy.set_printoptions(threshold = numpy.inf)

diag = False
if len(sys.argv) >= 2 and sys.argv[1] == '--diag':
  diag = True
  del sys.argv[1]
if len(sys.argv) < 2:
  print(f'usage: {sys.argv[0]} rtheta_to_xy_fit_out.yml')
  sys.exit(EXIT_FAILURE)
rtheta_to_xy_fit_out = sys.argv[1]

# function to be approximated
def f(x):
  return mpmath.matrix(
    [mpmath.cos(x[i]) for i in range(x.rows)]
  )
def g(x):
  return mpmath.matrix(
    [mpmath.sin(x[i]) for i in range(x.rows)]
  )
a = -.25 * math.pi
b = .25 * math.pi

# find approximating polynomial
p, _, p_err = utils.remez.remez_even(f, b, ORDER1, ERR_ORDER)
p = numpy.array(p, numpy.double)
p_err = float(p_err)
q, _, q_err = utils.remez.remez_odd(
  g,
  b,
  ORDER2,
  ERR_ORDER,
  epsilon = EPSILON
)
q = numpy.array(q, numpy.double)
q_err = float(q_err)

# checking
if diag:
  import matplotlib.pyplot
  import utils.poly

  x = numpy.linspace(a, b, 1000, numpy.double)
  matplotlib.pyplot.plot(
    x,
    numpy.array(f(mpmath.matrix(x)), numpy.double)
  )
  matplotlib.pyplot.plot(
    x,
    numpy.array(
      utils.poly.eval_multi(mpmath.matrix(p), mpmath.matrix(x ** 2)),
      numpy.double
    )
  )
  matplotlib.pyplot.plot(
    x,
    numpy.array(g(mpmath.matrix(x)), numpy.double)
  )
  matplotlib.pyplot.plot(
    x,
    numpy.array(
      utils.poly.eval_multi(mpmath.matrix(q), mpmath.matrix(x ** 2)),
      numpy.double
    ) * x
  )
  matplotlib.pyplot.show()

utils.yaml_io.write_file(
  rtheta_to_xy_fit_out,
  utils.yaml_io.export(
    {
      'a': a,
      'b': b,
      'p': p,
      'p_err': p_err,
      'q': q,
      'q_err': q_err
    }
  )
)
