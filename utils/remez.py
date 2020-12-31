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

import mpmath
import utils.poly
import utils.poly_fit

EPSILON = 1e-6

# Remez algorithm -- fit function f to polynomial p of given order
# f is not fitted directly but via a polynomial approximation of order err_order
# err_rel determines error weighting based on x^err_rel, as follows:
#   -1 inverse relative error (used for fitting odd functions)
#   0 absolute error
#   1 relative error
def remez(
  f,
  a,
  b,
  order,
  err_order,
  err_rel = 0,
  iters = 10
):
  # put minimax nodes halfway between Chebyshev nodes on unit circle
  x = a + (b - a) * (
    .5 + .5 * mpmath.matrix(
      [
        mpmath.cos(i * mpmath.pi / order)
        for i in range(order + 1)
      ]
    )
  )
  print('x', x)
  for i in range(iters):
    print('i', i)

    # let p be approximating polynomial, fitted to nodes with oscillation
    y = f(x)
    #print('y', y)
    A = mpmath.matrix(order + 1)
    A[:, :order] = utils.poly_fit.vandermonde(x, order)
    for i in range(order + 1):
      A[i, order] = (1 - 2 * (i & 1)) * x[i] ** err_rel
    #print('A', A)
    p = mpmath.lu_solve(A, y)
    osc = p[p.rows - 1]
    print('osc', osc)
    p = p[:-1]
    #print('p', p)

    # let q be the error function
    def g(x):
      y = utils.poly.eval_multi(p, x) - f(x)
      return mpmath.matrix(
        [
          y[i] * x[i] ** -err_rel
          for i in range(y.rows)
        ]
      )
    q = utils.poly_fit.any_f_to_poly(g, a, b, err_order)
    #print('q', q)
    print('q(x)', utils.poly.eval_multi(q, x))

    # partition domain into intervals where q is positive or negative
    intervals = utils.poly.real_roots(q, a, b)
    print('intervals', intervals)
    n_intervals = intervals.rows - 1
    print('n_intervals', n_intervals)
    if n_intervals < order + 1:
      # there absolutely have to be at least order + 1 intervals,
      # because the oscillating fit made q go positive and negative,
      # if there isn't, it means osc is very tiny or precision error
      #print('warning: not enough intervals -- we say good enough')
      #break
      assert False

    # determine if q increasing or decreasing through each boundary
    # have n_intervals - 1 boundaries, must produce n_intervals signs,
    # then check that the intervals are actually alternating in sign
    interval_pos = utils.poly.eval_multi(
      utils.poly.deriv(q),
      intervals[1:-1]
    )
    interval_pos = [interval_pos[i] >= 0. for i in range(interval_pos.rows)]
    #print('interval_pos', interval_pos)
    interval_polarity = not interval_pos[0] # sign of first interval
    #print('interval_polarity', interval_polarity)
    if any(
      [
        interval_pos[i] ^ bool(i & 1) == interval_polarity
        for i in range(len(interval_pos))
      ]
    ):
      # see above
      #print('warning: intervals not alternating -- we say good enough')
      #break
      assert False

    # within each interval, find the "global" maximum or minimum of q
    interval_extrema = utils.poly.interval_extrema(q, intervals)
    x = []
    y = []
    for i in range(n_intervals):
      extrema_x, extrema_y = interval_extrema[i]
      #print('i', i, 'extrema_x', extrema_x, 'extrema_y', extrema_y)
      j = 0
      if (i & 1) == interval_polarity:
        for k in range(1, extrema_y.rows):
          if extrema_y[k] < extrema_y[j]:
            j = k
      else:
        for k in range(1, extrema_y.rows):
          if extrema_y[k] > extrema_y[j]:
            j = k
      x.append(extrema_x[j])
      y.append(extrema_y[j])
    x = mpmath.matrix(x)
    print('x', x)
    y = mpmath.matrix(y)
    print('y', y)

    # trim off unwanted intervals, extra intervals can occur at either end
    # (the fit can walk left or right in the domain, discovering new nodes)
    while n_intervals > order + 1:
      if abs(y[0]) >= abs(y[-1]):
        print('trim right')
        x = x[:-1]
        y = y[:-1]
      else:
        print('trim left')
        x = x[1:]
        y = y[1:]
      n_intervals -= 1

    # checking
    err = utils.poly.eval_multi(q, x)
    print('err', err)

  # final minimax error analysis
  def g(x):
    y = utils.poly.eval_multi(p, x) - f(x)
    return mpmath.matrix(
      [
        y[i] * x[i] ** -err_rel
        for i in range(y.rows)
      ]
    )
  q = utils.poly_fit.any_f_to_poly(g, a, b, err_order)
  #print('q', q)
  #print('q(x)', utils.poly.eval_multi(q, x))
  _, y = utils.poly.extrema(q, a, b)
  err = max([abs(y[i]) for i in range(y.rows)])
  print('err', err)

  return p, x, err

# fit even polynomial in a domain symmetrical about 0
# fits order * 2 polynomial, returns order even coefficients
def remez_even(
  f,
  b,
  order,
  err_order,
  err_rel = 0,
  iters = 10
):
  def g(x):
    return f(
      mpmath.matrix(
        [mpmath.sqrt(x[i]) for i in range(x.rows)]
      )
    )
  return remez(
    g,
    0.,
    b ** 2,
    order,
    err_order,
    err_rel,
    iters
  )

# fit odd polynomial in a domain symmetrical about 0
# fits order * 2 + 1 polynomial, returns order odd coefficients
# function won't be evaluated at 0, domain will start at EPSILON instead
# (because we don't have a way to take the limiting value of f(x) / x at 0)
def remez_odd(
  f,
  b,
  order,
  err_order,
  err_rel = 0,
  iters = 10,
  epsilon = EPSILON
):
  def g(x):
    x = mpmath.matrix(
      [mpmath.sqrt(x[i]) for i in range(x.rows)]
    )
    y = f(x)
    return mpmath.matrix(
      [y[i] / x[i] for i in range(x.rows)]
    )
  return remez(
    g,
    epsilon ** 2,
    b ** 2,
    order,
    err_order,
    err_rel - 1,
    iters
  )
