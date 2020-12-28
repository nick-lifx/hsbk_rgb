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
import sys
from numpy_to_python import numpy_to_python
from python_to_numpy import python_to_numpy

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

ORDER1 = 4
ORDER2 = 3
ERR_ORDER = 16
EPSILON = 1e-4

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

# function to be approximated
f = numpy.cos
g = numpy.sin
a = -.25 * math.pi
b = .25 * math.pi

# find approximating polynomial
p, _, p_err = remez.remez_even(f, b, ORDER1, ERR_ORDER)
q, _, q_err = remez.remez_odd(g, b, ORDER2, ERR_ORDER, epsilon = EPSILON)

# checking
if diag:
  import matplotlib.pyplot

  x = numpy.linspace(a, b, 1000, numpy.double)
  matplotlib.pyplot.plot(x, f(x))
  matplotlib.pyplot.plot(x, poly.eval(p, x ** 2))
  matplotlib.pyplot.plot(x, g(x))
  matplotlib.pyplot.plot(x, poly.eval(q, x ** 2) * x)
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
