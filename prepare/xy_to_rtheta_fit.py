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
import remez
import ruamel.yaml
import sys
from numpy_to_python import numpy_to_python
from python_to_numpy import python_to_numpy

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

ERR_ORDER = 24
ORDER1 = 7
ORDER2 = 7
EPSILON = 1e-4

diag = False
if len(sys.argv) >= 2 and sys.argv[1] == '--diag':
  diag = True
  del sys.argv[1]
if len(sys.argv) < 2:
  print(f'usage: {sys.argv[0]} xy_to_rtheta_fit_out.yml')
  sys.exit(EXIT_FAILURE)
xy_to_rtheta_fit_out = sys.argv[1]

yaml = ruamel.yaml.YAML(typ = 'safe')
#numpy.set_printoptions(threshold = numpy.inf)

# function to be approximated
def f(x):
  return numpy.sqrt(x ** 2 + 1.)
g = numpy.arctan
a = -1.
b = 1.

# find approximating polynomial
p, p_err = remez.remez_even(f, b, ORDER1, ERR_ORDER)
q, q_err = remez.remez_odd(g, b, ORDER2, ERR_ORDER, a_epsilon = EPSILON)

# checking
if diag:
  import matplotlib.pyplot

  x = numpy.linspace(a, b, 1000, numpy.double)
  matplotlib.pyplot.plot(x, f(x))
  matplotlib.pyplot.plot(x, poly.eval(p, x ** 2))
  matplotlib.pyplot.plot(x, g(x))
  matplotlib.pyplot.plot(x, poly.eval(q, x ** 2) * x)
  matplotlib.pyplot.show()

xy_to_rtheta_fit = {
  'a': a,
  'b': b,
  'p': p,
  'p_err': float(p_err),
  'q': q,
  'q_err': float(q_err)
}
with open(xy_to_rtheta_fit_out, 'w') as fout:
  yaml.dump(numpy_to_python(xy_to_rtheta_fit), fout)
