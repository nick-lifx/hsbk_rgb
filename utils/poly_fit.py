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

import mpmath
import utils.poly

EPSILON = 1e-12

# return a matrix with one row per x-value, and "order" columns
# each row consists of the powers 0, 1, ..., order - 1 of the given x-value
def vandermonde(x, order):
  A = mpmath.matrix(x.rows, order)
  A[:, 0] = 1.
  for i in range(x.rows):
    for j in range(1, order):
      A[i, j] = A[i, j - 1] * x[i]
  return A

# return a polynomial p of order "order", such that p(x) = y
def fit(x, y, order):
  a = min(x)
  b = max(x)

  # remap [a, b] to [-1, 1] for better conditioning
  p = mpmath.lu_solve(
    vandermonde(mpmath.matrix([a, b]), 2),
    mpmath.matrix([-1., 1.])
  )

  # fit polynomial to remapped x, then compose with mapping function
  q = utils.poly.compose(
    mpmath.lu_solve(
      vandermonde(utils.poly.eval_multi(p, x), order),
      y
    ),
    p
  )

  # checking
  #err = utils.poly.eval_multi(x) - y
  #print('err', err)

  return q

# return a polynomial p such that p(x) == f(x) at the Chebyshev points
def any_f_to_poly(f, a, b, order):
  # remap [a, b] to [-1, 1] for better conditioning
  p = mpmath.lu_solve(
    vandermonde(mpmath.matrix([a, b]), 2),
    mpmath.matrix([-1., 1.])
  )

  # fit polynomial to [-1, 1], then compose with mapping function
  p_x = mpmath.matrix(
    [mpmath.cos((i + .5) * mpmath.pi / order) for i in range(order)]
  )
  x = mpmath.matrix(
    [a + (b - a) * (.5 + .5 * p_x[i]) for i in range(order)]
  )
  q = utils.poly.compose(
    mpmath.lu_solve(vandermonde(p_x, order), f(x)),
    p
  )

  # checking
  p_x = mpmath.matrix(
    [mpmath.cos(i * mpmath.pi / order) for i in range(order + 1)]
  )
  x = mpmath.matrix(
    [a + (b - a) * (.5 + .5 * p_x[i]) for i in range(order + 1)]
  )
  y = utils.poly.eval_multi(q, x) - f(x)
  est_err = max([abs(y[i]) for i in range(y.rows)])
  print('est_err', est_err)

  return q
