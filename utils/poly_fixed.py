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
  exp = numpy.array(
    [
      max(
        [
          mpmath.frexp(j * (1 + epsilon))[1]
          for j in utils.poly._range(p[i:], a, b)
        ]
      )
      for i in range(p.rows)
    ],
    numpy.int32
  )
  p_exp = numpy.array(
    [
      mpmath.frexp(p[i] * (1 + epsilon))[1]
      for i in range(p.rows - 1)
    ],
    numpy.int32
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
      [mpmath.ldexp(p[i], int(-exp[i])) for i in range(p.rows)]
    ),
    shr,
    exp[0]
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
    [mpmath.ldexp(c[i] + .5, int(shr[i])) for i in range(c.rows - 1)] +
      [c[c.rows - 1]]
  )
  return numpy.array(
    [int(mpmath.nint(c[i])) for i in range(c.rows)],
    dtype
  )

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
   c, shr, exp = align(p, a, b, x_exp, bits, y_exp, epsilon)
   c = quantize(c, shr, dtype)
   return c, shr, exp
