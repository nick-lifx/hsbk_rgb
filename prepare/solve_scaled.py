import numpy
import numpy.linalg

def solve_scaled(A, b):
  col_scale = numpy.sqrt(numpy.sum(numpy.square(A), 0))
  return numpy.linalg.solve(
    A / col_scale[numpy.newaxis, :],
    b
  ) / (
    col_scale if len(b.shape) == 1 else col_scale[:, numpy.newaxis]
  )
