import numpy

def python_to_numpy(value, dtype = numpy.double):
  return (
    numpy.array(value, dtype)
  if isinstance(value, list) else
    {i: python_to_numpy(j, dtype) for i, j in value.items()}
  if isinstance(value, dict) else
    value
  )
