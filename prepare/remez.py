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

EPSILON = 1e-12

# Remez algorithm -- fit polynomial q of given order to polynomial p
def remez(p, a, b, order, iters = 10, epsilon = EPSILON):
  # put minimax nodes halfway between Chebyshev nodes on unit circle
  x = a + (b - a) * (
    .5 + .5 * numpy.cos(
      numpy.arange(order + 1, dtype = numpy.int32) * math.pi / order
    )
  )
  print('x', x)
  for i in range(iters):
    print('i', i)

    # let q be approximating polynomial, fitted to nodes with oscillation
    y = poly.eval(p, x)
    #print('y', y)
    q = numpy.linalg.solve(
      numpy.concatenate(
        [
          x[:, numpy.newaxis] ** numpy.arange(order, dtype = numpy.int32),
          (
            (-1.) ** numpy.arange(order + 1, dtype = numpy.int32)
          )[:, numpy.newaxis]
        ],
        1
      ),
      y
    )
    osc = q[-1]
    print('osc', osc)
    q = q[:-1]
    print('q', q)

    # let r be the error function
    r = poly.add(q, -p)
    #print('r', r)
    #print('r(x)', poly.eval(r, x))

    # partition domain into intervals where r is positive or negative
    intervals = poly.real_roots(r, a, b, epsilon)
    print('intervals', intervals)
    n_intervals = intervals.shape[0] - 1
    print('n_intervals', n_intervals)
    if n_intervals < order + 1:
      # there absolutely have to be at least order + 1 intervals,
      # because the oscillating fit made p go positive and negative,
      # if there isn't, it means osc is very tiny or precision error
      print('warning: not enough intervals -- we say good enough')
      break

    # determine if r increasing or decreasing through each boundary
    # have n_intervals - 1 boundaries, must produce n_intervals signs
    # then check that the intervals are actually alternating in sign
    interval_pos = poly.eval(poly.deriv(r), intervals[1:-1]) >= 0.
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

    # within each interval, find the "global" maximum or minimum of r
    interval_extrema = poly.interval_extrema(r, intervals, epsilon)
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
  print('q', q)

  # final minimax error analysis
  _, y = poly.extrema(poly.add(q, -p), a, b, epsilon)
  err = numpy.max(numpy.abs(y))
  print('err', err)

  return q, err
