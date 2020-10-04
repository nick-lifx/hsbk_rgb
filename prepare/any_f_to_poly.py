import math
import numpy
import numpy.linalg
import poly

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
  print('x', x)
  y = f(x)
  print('y', y)
  p = numpy.linalg.solve(
    x[:, numpy.newaxis] ** numpy.arange(order, dtype = numpy.int32),
    y
  )
  print('p', p)

  # checking
  x = a + (b - a) * (
    .5 + .5 * numpy.cos(
      numpy.arange(order + 1, dtype = numpy.int32) * math.pi / order
    )
  )
  print('x', x)
  err = poly.eval(p, x) - f(x)
  print('err', err)

  return p
