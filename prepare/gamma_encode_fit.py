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
import numpy.linalg
import math
import poly
import ruamel.yaml
import sys
from any_f_to_poly import any_f_to_poly
from numpy_to_python import numpy_to_python
from python_to_numpy import python_to_numpy
from remez import remez

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

ORDER0 = 24
ORDER1 = 8
EPSILON = 1e-12

diag = False
if len(sys.argv) >= 2 and sys.argv[1] == '--diag':
  diag = True
  del sys.argv[1]
if len(sys.argv) < 2:
  print(f'usage: {sys.argv[0]} gamma_encode_fit_out.yml')
  sys.exit(EXIT_FAILURE)
gamma_encode_fit_out = sys.argv[1]

yaml = ruamel.yaml.YAML(typ = 'safe')
#numpy.set_printoptions(threshold = numpy.inf)

# function to be approximated
def f(x):
  return x ** (1. / 2.4) * 1.055
a = .0031308
b = 1.

# to use:
# def gamma_encode(x):
#   return x * 12.92 if x .0031308 else f(x) - .055

# find approximating polynomial
p, err = remez(any_f_to_poly(f, .5, 1., ORDER0), .5, 1., ORDER1)

# compute pre- and post-processing constants

# find exp0, exp1 to guarantee that argument is in range [2^exp0, 2^exp1]
_, exp0 = math.frexp(a * (1. - EPSILON))
_, exp1 = math.frexp(b * (1. + EPSILON))

# given argument is pre-multiplied by 2^-i, find compensating post-factor
post_factor = numpy.array(
  [
    math.ldexp(1., -i) ** -(1. / 2.4)
    for i in range(exp0, exp1 + 1)
  ],
  numpy.double
)

# checking
if diag:
  import matplotlib.pyplot

  def g(x):
    x, exp = numpy.frexp(x)
    return poly.eval(p, x) * post_factor[exp - exp0]

  x = numpy.linspace(a, b, 1000, numpy.double)
  matplotlib.pyplot.plot(x, f(x))
  matplotlib.pyplot.plot(x, g(x))
  matplotlib.pyplot.show()

gamma_encode_fit = {
  'a': a,
  'b': b,
  'p': p,
  'err': float(err),
  'exp0': exp0,
  'exp1': exp1,
  'post_factor': post_factor
}
with open(gamma_encode_fit_out, 'w') as fout:
  yaml.dump(numpy_to_python(gamma_encode_fit), fout)
