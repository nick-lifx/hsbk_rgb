import numpy
import numpy.linalg

# the same as numpy.linalg.solve, but tries to condition the matrix better
# the matrix it not allowed to contain zeros (usually a Vandermonde matrix)
def solve_scaled(A, b):
  col_scale = numpy.min(numpy.abs(A), 0) ** -.5
  row_scale = numpy.min(numpy.abs(A), 1) ** -.5
  return numpy.linalg.solve(
    A * (col_scale[numpy.newaxis, :] * row_scale[:, numpy.newaxis]),
    b * row_scale
  ) * col_scale
