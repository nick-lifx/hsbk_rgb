import mpmath
import numpy

# compatible replacements for numpy functions, with improved accuracy
mpmath.mp.prec = 212

def lstsq(A, b):
  col_scale = numpy.sqrt(numpy.sum(numpy.square(A), 0))
  return numpy.array(
    mpmath.lu_solve(
      mpmath.matrix(A / col_scale[numpy.newaxis, :]),
      mpmath.matrix(b)
    ),
    numpy.double
  ) / (
    col_scale if len(b.shape) == 1 else col_scale[:, numpy.newaxis]
  )

def solve(A, b):
  assert A.shape[0] == A.shape[1]
  return lstsq(A, b)
