#!/usr/bin/env python3
# generated by ../prepare/gamma_decode_gen_py.py

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
# minimax error is up to 1.187446e-08 relative
def gamma_decode(x):
  if x < 4.0449935999999999e-02:
    return x * 7.7399380804953566e-02
  x, exp = math.frexp(x + .055)
  assert exp < 2
  y = -1.2846808623510494e-02
  y = y * x + 7.8691179412618065e-02
  y = y * x - 2.3343876197438471e-01
  y = y * x + 6.0014713976457434e-01
  y = y * x + 4.8334146749135826e-01
  y = y * x - 3.9149281499659572e-02
  y = y * x + 2.6705149567045200e-03
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
