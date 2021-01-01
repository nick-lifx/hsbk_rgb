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

N_ITERS = 5
EXTRA_ORDER = 8
EPSILON = 1e-6

# Remez algorithm -- fit a lower degree polynomial to a higher degree one
# err_rel determines error weighting based on x^err_rel, as follows:
#   -1 inverse relative error (used for fitting odd functions)
#   0 absolute error
#   1 relative error
def remez(
  p,
  a,
  b,
  order,
  err_rel = 0,
  n_iters = N_ITERS
):
  # remap [a, b] to [-1, 1] for better conditioning
  q = mpmath.lu_solve(
    utils.poly_fit.vandermonde(mpmath.matrix([a, b]), 2),
    mpmath.matrix([-1., 1.])
  )

  # put minimax nodes halfway between Chebyshev nodes on unit circle
  q_x = mpmath.matrix(
    [mpmath.cos(i * mpmath.pi / order) for i in range(order + 1)]
  )
  x = mpmath.matrix(
    [a + (b - a) * (.5 + .5 * q_x[i]) for i in range(order + 1)]
  )
  #print('x', x)
  i = 0
  while True:
    #print('i', i)

    # let r be approximating polynomial, fitted to nodes with oscillation
    y = utils.poly.eval_multi(p, x)
    #print('y', y)
    A = mpmath.matrix(order + 1)
    q_x = utils.poly.eval_multi(q, x)
    A[:, :order] = utils.poly_fit.vandermonde(q_x, order)
    for j in range(order + 1):
      A[j, order] = (1 - 2 * (j & 1)) * x[j] ** err_rel
    #print('A', A)
    r = mpmath.lu_solve(A, y)
    osc = r[r.rows - 1]
    print('i', i, 'osc', osc)
    r = utils.poly.compose(r[:-1], q)
    #print('r', r)

    # let s be the error function
    s = utils.poly.add(r, -p)
    #print('s', s)
    if i >= n_iters:
      break

    # partition domain into intervals where s is positive or negative
    intervals = utils.poly.real_roots(s, a, b)
    #print('intervals', intervals)
    n_intervals = intervals.rows - 1
    #print('n_intervals', n_intervals)
    if n_intervals < order + 1:
      # there absolutely have to be at least order + 1 intervals,
      # because the oscillating fit made r go positive and negative,
      # if there isn't, it means osc is very tiny or precision error
      #print('warning: not enough intervals -- we say good enough')
      #break
      assert False

    # determine if s increasing or decreasing through each boundary
    # have n_intervals - 1 boundaries, must produce n_intervals signs,
    # then check that the intervals are actually alternating in sign
    interval_pos = utils.poly.eval_multi(
      utils.poly.deriv(s),
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

    # within each interval, find the "global" maximum or minimum of s
    interval_extrema = utils.poly.interval_extrema(s, intervals)
    x = []
    y = []
    for j in range(n_intervals):
      extrema_x, extrema_y = interval_extrema[j]
      #print('j', j, 'extrema_x', extrema_x, 'extrema_y', extrema_y)
      k = 0
      if (j & 1) == interval_polarity:
        for l in range(1, extrema_y.rows):
          if extrema_y[l] < extrema_y[k]:
            k = l
      else:
        for l in range(1, extrema_y.rows):
          if extrema_y[l] > extrema_y[k]:
            k = l
      x.append(extrema_x[k])
      y.append(extrema_y[k])
    x = mpmath.matrix(x)
    #print('x', x)
    y = mpmath.matrix(y)
    #print('y', y)

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
    #err = utils.poly.eval_multi(s, x)
    #print('err', err)
    i += 1

  # final minimax error analysis
  _, y = utils.poly.extrema(s, a, b)
  err = max([abs(y[i]) for i in range(y.rows)])
  print('err', err)

  return r, err

# given an arbitrary function, find an approximating polynomial of
# a safely high order, and then fit to the approximating polynomial
def remez_f(
  f,
  a,
  b,
  order,
  err_rel = 0,
  n_iters = N_ITERS,
  extra_order = EXTRA_ORDER
):
  return remez(
    utils.poly_fit.any_f_to_poly(
      f,
      a,
      b,
      order + extra_order
    ),
    a,
    b,
    order,
    err_rel,
    n_iters
  )

# fit even polynomial in a domain symmetrical about 0
# fits order * 2 polynomial, returns order even coefficients
def remez_even_f(
  f,
  b,
  order,
  err_rel = 0,
  n_iters = N_ITERS,
  extra_order = EXTRA_ORDER
):
  def g(x):
    x = mpmath.matrix(
      [mpmath.sqrt(x[i]) for i in range(x.rows)]
    )
    return f(x)
  return remez_f(
    g,
    0.,
    b ** 2,
    order,
    err_rel,
    n_iters,
    extra_order
  )

# fit odd polynomial in a domain symmetrical about 0
# fits order * 2 + 1 polynomial, returns order odd coefficients
# function won't be evaluated at 0, domain will start at EPSILON instead
# (because we don't have a way to take the limiting value of f(x) / x at 0)
def remez_odd_f(
  f,
  b,
  order,
  err_rel = 0,
  n_iters = N_ITERS,
  extra_order = EXTRA_ORDER,
  epsilon = EPSILON,
):
  def g(x):
    x = mpmath.matrix(
      [mpmath.sqrt(x[i]) for i in range(x.rows)]
    )
    y = f(x)
    return mpmath.matrix(
      [y[i] / x[i] for i in range(x.rows)]
    )
  return remez_f(
    g,
    epsilon ** 2,
    b ** 2,
    order,
    err_rel - 1,
    n_iters,
    extra_order
  )
