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
import poly

EPSILON = 1e-8

# routines for converting polynomial coefficients to fixed point

# find range of each sub-polynomial encountered in Horner's rule evaluation,
# then calculate the exponent needed to represent that range (or the exponent
# needed to prevent the next coefficient from overflowing, whichever larger)
def intermediate_exp(p, a, b, epsilon = EPSILON):
  _, exp = numpy.frexp(
    numpy.array(
      [poly._range(p[i:], a, b) for i in range(p.shape[0])],
      numpy.double
    ) * (1. + epsilon)
  )
  exp = numpy.max(exp, 1)
  _, p_exp = numpy.frexp(p[:-1])
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
  return numpy.ldexp(p, -exp), shr, exp[0]

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
  c = numpy.copy(c)
  c[:-1] = numpy.ldexp(c[:-1] + .5, shr)
  return numpy.round(c).astype(dtype)

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
