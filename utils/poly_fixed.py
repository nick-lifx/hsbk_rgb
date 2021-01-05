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
import numpy
import utils.poly

EPSILON = 1e-8

# routines for converting polynomial coefficients to fixed point

# find range of each sub-polynomial encountered in Horner's rule evaluation,
# then calculate the exponent needed to represent that range (or the exponent
# needed to prevent the next coefficient from overflowing, whichever larger)
def intermediate_exp(p, a, b, epsilon = EPSILON):
  exp = numpy.max(
    numpy.array(
      [
        [
          max(
            [
              mpmath.frexp(k * (1 + epsilon))[1]
              for k in utils.poly._range(p[i, j:].transpose(), a[i], b[i])
            ]
          )
          for j in range(p.cols)
        ]
        for i in range(p.rows)
      ],
      numpy.int32
    ),
    0
  )
  p_exp = numpy.max(
    numpy.array(
      [
        [
          mpmath.frexp(p[i, j] * (1 + epsilon))[1]
          for j in range(p.cols - 1)
        ]
        for i in range(p.rows)
      ],
      numpy.int32
    ),
    0
  )
  exp[1:] = numpy.maximum(exp[1:], p_exp)
  return exp

# find exponents of intermediate results during Horner's rule evaluation,
# (ensuring intermediate result is at least as big as the next coefficient)
# then find shift amounts to align each intermediate result with next stage
# (the shift also removes the effect of the independent variable exponent)
# return the aligned cofficients, the shifts, and exponent of final result
def align(p, a, b, x_exp, bits, y_exp = None, epsilon = EPSILON):
  exp = intermediate_exp(p, a, b, epsilon) - bits
  if y_exp is not None:
    assert exp[0] <= y_exp
    exp[0] = y_exp
  #print('exp', exp)
  shr = exp[:-1] - exp[1:] - x_exp
  #print('shr', shr)
  return (
    mpmath.matrix(
      [
        [
          mpmath.ldexp(p[i, j], int(-exp[j]))
          for j in range(p.cols)
        ]
        for i in range(p.rows)
      ]
    ),
    shr,
    exp
  )

# if we round the coefficients to integer as-is, the algorithm would be
#   y = c[-1]
#   y = round(ldexp(y * x, -shr[-1])) + c[-2]
#   y = round(ldexp(y * x, -shr[-2])) + c[-3]
#   ...
# or, if we move the coefficients inside the round() then it would be
#   y = c[-1]
#   y = round(ldexp(y * x, -shr[-1]) + c[-2])
#   y = round(ldexp(y * x, -shr[-2]) + c[-3])
#   ...
# this lets us add an offset of .5 to each coefficient and use floor()
#   y = c[-1]
#   y = floor(ldexp(y * x, -shr[-1]) + c[-2])
#   y = floor(ldexp(y * x, -shr[-2]) + c[-3])
#   ...
# and we then move coefficients inside ldexp(), shifting to compensate
#   y = c[-1]
#   y = floor(ldexp(y * x + c[-2], -shr[-1])
#   y = floor(ldexp(y * x + c[-3], -shr[-2])
#   ...
# then provided the shr is at least 1, the coefficients can be integer
def quantize(c, shr, dtype = numpy.int64):
  assert numpy.all(shr >= 1)
  c = mpmath.matrix(
    [
      [
        mpmath.ldexp(c[i, j] + .5, int(shr[j]))
        for j in range(c.cols - 1)
      ] +
        [c[i, c.cols - 1]]
      for i in range(c.rows)
    ]
  )
  return numpy.array(
    [
      [
        int(mpmath.nint(c[i, j]))
        for j in range(c.cols)
      ]
      for i in range(c.rows)
    ],
    dtype
  )

# perform a range analysis of each polynomial on the interval [a, b] which
# is given separately per polynomial; also analyze the intermediate products
# when evaluated by Horner's rule, and figure out the fixed-point exponent
# at each stage -- then resolve it to a set of 64-bit add-and-shift operations
# inputs are in mpmath format:
#   p is a matrix with one polynomial per row, a and b are column vectors
# independent variable a <= x <= b is an integer interpreted as x 2^x_exp
# dependent variable (result of evaluation) will be an integer interpreted as
# y 2^y_exp, except if y_exp is None, in which case it will be determined
# automatically based on its range in the same way as intermediate products
# outputs are in numpy format:
#   c is the same size as p and contains 64-bit integer coefficients, except
#   the last which is a 32-bit coefficient (already rounded, as it's constant)
#   shr is a vector with shr.shape[0] == c.shape[1] - 1 and gives the amount
#   to shift in between each stage (c has added 0.5 offset to provide rounding)
#   exp is a vector with exp.shape[0] == c.shape[1] and gives an exponent that
#   allows to interpret the intermediate 32-bit integer product after >> by shr
#   (exp[0] == y_exp if y_exp was provided, otherwise inspect it to find y_exp)
def poly_fixed_multi(
  p,
  a,
  b,
  x_exp,
  bits,
  y_exp = None,
  dtype = numpy.int64,
  epsilon = EPSILON
):
   c, shr, exp = align(p, a, b, x_exp, bits, y_exp, epsilon)
   c = quantize(c, shr, dtype)
   return c, shr, exp

# same but p, c are vectors and a, b are scalars, only does one polynomial
def poly_fixed(
  p,
  a,
  b,
  x_exp,
  bits,
  y_exp = None,
  dtype = numpy.int64,
  epsilon = EPSILON
):
  c, shr, exp = poly_fixed_multi(
    p.transpose(),
    mpmath.matrix([a]),
    mpmath.matrix([b]),
    x_exp,
    bits,
    y_exp,
    dtype,
    epsilon
  )
  return c[0, :], shr, exp
