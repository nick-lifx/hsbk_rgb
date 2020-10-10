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

ORDER0 = 16
ORDER1 = 4
ORDER2 = 3
EPSILON = 1e-8

diag = False
if len(sys.argv) >= 2 and sys.argv[1] == '--diag':
  diag = True
  del sys.argv[1]
if len(sys.argv) < 2:
  print(f'usage: {sys.argv[0]} rtheta_to_xy_fit_out.yml')
  sys.exit(EXIT_FAILURE)
rtheta_to_xy_fit_out = sys.argv[1]

yaml = ruamel.yaml.YAML(typ = 'safe')
#numpy.set_printoptions(threshold = numpy.inf)

def f(x):
  x = numpy.sqrt(x)
  return numpy.cos(x)
def g(x):
  x = numpy.sqrt(x)
  return numpy.sin(x) / x
a = 0.
a_eps = EPSILON
b = (.25 * math.pi) ** 2

# find approximating polynomial
p, p_err = remez(any_f_to_poly(f, a, b, ORDER0), a, b, ORDER1)
q, q_err = remez(any_f_to_poly(g, a_eps, b, ORDER0), a_eps, b, ORDER2, times_x = True)

# checking
if diag:
  import matplotlib.pyplot

  def f1(x):
    return poly.eval(p, x)
  def g1(x):
    return poly.eval(q, x)

  x = numpy.linspace(math.sqrt(a_eps), math.sqrt(b), 1000, numpy.double)
  matplotlib.pyplot.plot(x, f(x ** 2))
  matplotlib.pyplot.plot(x, f1(x ** 2))
  matplotlib.pyplot.plot(x, g(x ** 2) * x)
  matplotlib.pyplot.plot(x, g1(x ** 2) * x)
  matplotlib.pyplot.show()

rtheta_to_xy_fit = {
  'a': a,
  'b': b,
  'p': p,
  'p_err': float(p_err),
  'q': q,
  'q_err': float(q_err)
}
with open(rtheta_to_xy_fit_out, 'w') as fout:
  yaml.dump(numpy_to_python(rtheta_to_xy_fit), fout)
