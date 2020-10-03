#!/usr/bin/env python3

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

ORDER0 = 21
ORDER1 = 7
EPSILON = 1e-12

diag = False
if len(sys.argv) >= 2 and sys.argv[1] == '--diag':
  diag = True
  del sys.argv[1]
if len(sys.argv) < 2:
  print(f'usage: {sys.argv[0]} gamma_decode_fit_out.yml')
  sys.exit(EXIT_FAILURE)
gamma_decode_fit_out = sys.argv[1]

yaml = ruamel.yaml.YAML(typ = 'safe')
#numpy.set_printoptions(threshold = numpy.inf)

# function to be approximated
def f(x):
  return (x / 1.055) ** 2.4
a = 12.92 * .0031308 + .055
b = 1.055

# to use:
# def gamma_decode(x):
#   return x / 12.92 if x < 12.92 * .0031308 else f(x + .055)

# find approximating polynomial
p, err = remez(any_f_to_poly(f, .5, 1., ORDER0), .5, 1., ORDER1)

# compute pre- and post-processing constants

# find exp0, exp1 to guarantee that argument is in range [2^exp0, 2^exp1]
_, exp0 = math.frexp(a * (1. - EPSILON))
_, exp1 = math.frexp(b * (1. + EPSILON))

# given argument is pre-multiplied by 2^-i, find compensating post-factor
post_factor = numpy.array(
  [
    math.ldexp(1., -i) ** -2.4
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