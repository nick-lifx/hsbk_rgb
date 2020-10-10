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

import math
import numpy
import numpy.linalg
import poly
from any_f_to_poly import any_f_to_poly

EPSILON = 1e-12
A_EPSILON = 1e-6

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
  iters = 10,
  epsilon = EPSILON
):
  # put minimax nodes halfway between Chebyshev nodes on unit circle
  x = a + (b - a) * (
    .5 + .5 * numpy.cos(
      numpy.arange(order + 1, dtype = numpy.int32) * math.pi / order
    )
  )
  print('x', x)
  for i in range(iters):
    print('i', i)

    # let p be approximating polynomial, fitted to nodes with oscillation
    y = f(x)
    #print('y', y)
    p = numpy.linalg.solve(
      numpy.concatenate(
        [
          x[:, numpy.newaxis] ** numpy.arange(order, dtype = numpy.int32),
          (
            (-1.) ** numpy.arange(order + 1, dtype = numpy.int32) *
              x ** err_rel
          )[:, numpy.newaxis]
        ],
        1
      ),
      y
    )
    osc = p[-1]
    print('osc', osc)
    p = p[:-1]
    print('p', p)

    # let q be the error function
    q = any_f_to_poly(
      lambda x: (poly.eval(p, x) - f(x)) * x ** -err_rel,
      a,
      b,
      err_order
    )
    #print('q', q)
    #print('q(x)', poly.eval(q, x))

    # partition domain into intervals where q is positive or negative
    intervals = poly.real_roots(q, a, b, epsilon)
    print('intervals', intervals)
    n_intervals = intervals.shape[0] - 1
    print('n_intervals', n_intervals)
    if n_intervals < order + 1:
      # there absolutely have to be at least order + 1 intervals,
      # because the oscillating fit made q go positive and negative,
      # if there isn't, it means osc is very tiny or precision error
      print('warning: not enough intervals -- we say good enough')
      break

    # determine if q increasing or decreasing through each boundary
    # have n_intervals - 1 boundaries, must produce n_intervals signs,
    # then check that the intervals are actually alternating in sign
    interval_pos = poly.eval(poly.deriv(q), intervals[1:-1]) >= 0.
    #print('interval_pos', interval_pos)
    interval_polarity = not interval_pos[0] # sign of first interval
    #print('interval_polarity', interval_polarity)
    if numpy.any(
      numpy.logical_xor(
        interval_pos,
        numpy.bitwise_and(
          numpy.arange(n_intervals - 1, dtype = numpy.int32),
          1
        ).astype(numpy.bool)
      ) == interval_polarity
    ):
      # see above
      print('warning: intervals not alternating -- we say good enough')
      break

    # within each interval, find the "global" maximum or minimum of q
    interval_extrema = poly.interval_extrema(q, intervals, epsilon)
    x = []
    y = []
    for i in range(n_intervals):
      extrema_x, extrema_y = interval_extrema[i]
      #print('i', i, 'extrema_x', extrema_x, 'extrema_y', extrema_y)
      j = (
        numpy.argmax if (i & 1) != interval_polarity else numpy.argmin
      )(extrema_y)
      x.append(extrema_x[j])
      y.append(extrema_y[j])
    x = numpy.array(x, numpy.double)
    print('x', x)
    y = numpy.array(y, numpy.double)
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
    err = poly.eval(q, x)
    print('err', err)

  # final minimax error analysis
  q = any_f_to_poly(
    lambda x: (poly.eval(p, x) - f(x)) * x ** -err_rel,
    a,
    b,
    err_order
  )
  #print('q', q)
  #print('q(x)', poly.eval(q, x))
  _, y = poly.extrema(q, a, b, epsilon)
  err = numpy.max(numpy.abs(y))
  print('err', err)

  return p, err

# fit even polynomial in a domain symmetrical about 0
# fits order * 2 polynomial, returns order even coefficients
def remez_even(
  f,
  b,
  order,
  err_order,
  err_rel = 0,
  iters = 10,
  epsilon = EPSILON
):
  def g(x):
    return f(numpy.sqrt(x))
  return remez(
    g,
    0.,
    b ** 2,
    order,
    err_order,
    err_rel,
    iters,
    epsilon
  )

# fit odd polynomial in a domain symmetrical about 0
# fits order * 2 + 1 polynomial, returns order odd coefficients
# function won't be evaluated at 0, domain will start at A_EPSILON instead
# (because we don't have a way to take the limiting value of f(x) / x at 0)
def remez_odd(
  f,
  b,
  order,
  err_order,
  err_rel = 0,
  iters = 10,
  epsilon = EPSILON,
  a_epsilon = A_EPSILON
):
  def g(x):
    x = numpy.sqrt(x)
    return f(x) / x
  return remez(
    g,
    a_epsilon ** 2,
    b ** 2,
    order,
    err_order,
    err_rel - 1,
    iters,
    epsilon
  )
