import numpy
import poly

SLOP = 1e-8
EPSILON = 1e-12

# routines for converting polynomial coefficients to fixed point

# find range of each sub-polynomial encountered in Horner's rule evaluation,
# return ceil of log2 of highest the magnitude of the endpoints of each range
def intermediate_exp(p, a, b, slop = SLOP, epsilon = EPSILON):
  _, exp = numpy.frexp(
    numpy.max(
      numpy.abs(
        numpy.array(
          [poly._range(p[i:], a, b, epsilon) for i in range(p.shape[0])],
          numpy.double
        )
      ),
      1
    ) * (1. + slop)
  )
  return exp

# find exponents of intermediate results during Horner's rule evaluation,
# then find shift amounts to align each intermediate result with next stage
# (the shift also removes the effect of the independent variable exponent)
# return the aligned cofficients, the shifts, and exponent of final result
def align(p, a, b, x_exp, bits, slop = SLOP, epsilon = EPSILON):
  exp = intermediate_exp(p, a, b, slop, epsilon) - bits
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
def quantize(c, shr):
  assert numpy.all(shr >= 1)
  c = numpy.copy(c)
  c[:-1] = numpy.ldexp(c[:-1] + .5, shr)
  return numpy.round(c).astype(numpy.int64)

def poly_fixed(p, a, b, x_exp, bits, slop = SLOP, epsilon = EPSILON):
   c, shr, exp = align(p, a, b, x_exp, bits, slop, epsilon)
   c = quantize(c, shr)
   return c, shr, exp
