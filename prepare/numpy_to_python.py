import numpy

def numpy_to_python(value, dtype = float):
  return (
    (
      [dtype(value[i]) for i in range(value.shape[0])]
    if len(value.shape) == 1 else
      [numpy_to_python(value[i], dtype) for i in range(value.shape[0])]
    )
  if isinstance(value, numpy.ndarray) else
    {i: numpy_to_python(j, dtype) for i, j in value.items()}
  if isinstance(value, dict) else
    value
  )
