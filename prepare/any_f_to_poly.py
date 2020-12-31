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

import linalg
import math
import mpmath
import numpy
import utils.poly

# convert any function to polynomial
# done by fitting to the Chebyshev points with no attempt at optimization,
# therefore you must use a high order for the errors to be insignificant;
# makes it easier to integrate, differentiate, find roots, maxima, minima,
# etc -- similar to chebfun package in matlab, except that we use ordinary
# monomial representation rather than the more numerically stable Chebyshev
def any_f_to_poly(f, a, b, order):
  x = a + (b - a) * (
    .5 + .5 * numpy.cos(
      (numpy.arange(order, dtype = numpy.int32) + .5) * math.pi / order
    )
  )
  #print('x', x)
  y = f(x)
  #print('y', y)
  p = linalg.solve(
    x[:, numpy.newaxis] ** numpy.arange(order, dtype = numpy.int32),
    y
  )
  #print('p', p)

  # checking
  x = a + (b - a) * (
    .5 + .5 * numpy.cos(
      numpy.arange(order + 1, dtype = numpy.int32) * math.pi / order
    )
  )
  #print('x', x)
  err = numpy.array(
    utils.poly.eval_multi(mpmath.matrix(p), mpmath.matrix(x)),
    numpy.double
  ) - f(x)
  print('err', err)

  return p
