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
import ruamel.yaml
import sys
from numpy_to_python import numpy_to_python
from python_to_numpy import python_to_numpy
from remez import remez

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

ORDER = 7
ERR_ORDER = 21
EPSILON = 1e-12

diag = False
if len(sys.argv) >= 2 and sys.argv[1] == '--diag':
  diag = True
  del sys.argv[1]
if len(sys.argv) < 3:
  print(f'usage: {sys.argv[0]} model_in.yml gamma_decode_fit_out.yml')
  sys.exit(EXIT_FAILURE)
model_in = sys.argv[1]
gamma_decode_fit_out = sys.argv[2]

yaml = ruamel.yaml.YAML(typ = 'safe')
#numpy.set_printoptions(threshold = numpy.inf)

with open(model_in) as fin:
  model = python_to_numpy(yaml.load(fin))
gamma_a = model['gamma_a']
gamma_b = model['gamma_b']
gamma_c = model['gamma_c']
gamma_d = model['gamma_d']
gamma_e = model['gamma_e']

# function to be approximated
def f(x):
  return (x / gamma_d) ** gamma_e
a = gamma_a * gamma_b + gamma_c
b = gamma_d

# to use:
# def gamma_decode(x):
#   return x / gamma_a if x < gamma_a * gamma_b else f(x + gamma_c)

# find approximating polynomial (relative error criterion)
p, _, err = remez(f, .5, 1., ORDER, ERR_ORDER, 1)

# compute pre- and post-processing constants

# find exp0, exp1 to guarantee that argument is in range [2^exp0, 2^exp1]
_, exp0 = math.frexp(a * (1. - EPSILON))
_, exp1 = math.frexp(b * (1. + EPSILON))

# given argument is pre-multiplied by 2^-i, find compensating post-factor
post_factor = numpy.array(
  [
    math.ldexp(1., -i) ** -gamma_e
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

gamma_decode_fit = {
  'gamma_a': gamma_a,
  'gamma_b': gamma_b,
  'gamma_c': gamma_c,
  'gamma_d': gamma_d,
  'gamma_e': gamma_e,
  'a': a,
  'b': b,
  'p': p,
  'err': float(err),
  'exp0': exp0,
  'exp1': exp1,
  'post_factor': post_factor
}
with open(gamma_decode_fit_out, 'w') as fout:
  yaml.dump(numpy_to_python(gamma_decode_fit), fout)
