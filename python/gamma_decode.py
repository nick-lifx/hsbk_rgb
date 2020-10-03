#!/usr/bin/env python3
# generated by ../prepare/gamma_decode_gen_py.py

import math
import numpy

post_factor = numpy.array(
  [
    6.8011762757509715e-03,
    3.5896823593657347e-02,
    1.8946457081379978e-01,
    1.0000000000000000e+00,
    5.2780316430915768e+00
  ],
  numpy.double
)

# returns approximation to:
#   x / 12.92 if x < 12.92 * .0031308 else ((x + .055) / 1.055) ** 2.4
# allowed domain (-inf, 1.945), recommended domain [-epsilon, 1 + epsilon]
# do not call with argument >= 1.945 due to table lookup overflow (unchecked)
# minimax error is up to 8.360670e-09 on domain [.445, .945]
def gamma_decode(x):
  if x < 4.0449935999999999e-02:
    return x * 7.7399380804953566e-02
  x, exp = math.frexp(x + .055)
  y = -1.2460692237447316e-02
  y = y * x + 7.6962587172054203e-02
  y = y * x - 2.3025054984246240e-01
  y = y * x + 5.9704727994557560e-01
  y = y * x + 4.8501673557167907e-01
  y = y * x - 3.9626343672606201e-02
  y = y * x + 2.7264361046669960e-03
  return y * post_factor[exp + 3]

if __name__ == '__main__':
  import sys

  EXIT_SUCCESS = 0
  EXIT_FAILURE = 1

  if len(sys.argv) < 2:
    print(f'usage: {sys.argv[0]:s} x')
    print('x = gamma encoded intensity, calculates linear intensity')
    sys.exit(EXIT_FAILURE)
  x = float(sys.argv[1])

  y = gamma_decode(x)
  print(f'gamma encoded {x:.6f} -> linear {y:.6f}')
