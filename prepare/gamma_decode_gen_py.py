#!/usr/bin/env python3

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

# put utils into path
# temporary until we have proper Python packaging
import os.path
import sys
dirname = os.path.dirname(__file__)
sys.path.append(os.path.join(dirname, '..'))

import mpmath
import numpy
import utils.yaml_io

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

mpmath.mp.prec = 106

#numpy.set_printoptions(threshold = numpy.inf)

if len(sys.argv) < 3:
  print(f'usage: {sys.argv[0]:s} gamma_decode_fit_in.yml device')
  sys.exit(EXIT_FAILURE)
gamma_decode_fit_in = sys.argv[1]
device = sys.argv[2]

gamma_decode_fit = utils.yaml_io._import(
  utils.yaml_io.read_file(gamma_decode_fit_in)
)
gamma_a = gamma_decode_fit['gamma_a']
gamma_b = gamma_decode_fit['gamma_b']
gamma_c = gamma_decode_fit['gamma_c']
gamma_d = gamma_decode_fit['gamma_d']
gamma_e = gamma_decode_fit['gamma_e']
p = gamma_decode_fit['p']
err = gamma_decode_fit['err']
exp0 = gamma_decode_fit['exp0']
exp1 = gamma_decode_fit['exp1']
post_factor = gamma_decode_fit['post_factor']

p = numpy.array(p, numpy.double)

print(
  '''#!/usr/bin/env python3
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
  [{0:s}
  ],
  numpy.double
)

# returns approximation to:
#   x / {1:s} if x < {2:s} * {3:s} else ((x + {4:s}) / {5:s}) ** {6:s}
# allowed domain (-inf, {7:s}), recommended domain [-epsilon, 1 + epsilon]
# do not call with argument >= {8:s} due to table lookup overflow (unchecked)
# minimax error is up to {9:e} relative
def gamma_decode_{10:s}(x):
  if x < {11:.16e}:
    return x * {12:.16e}
  x, exp = math.frexp(x + {13:.16e})
  assert exp < {14:d}
  y = {15:.16e}
{16:s}  return y * post_factor[exp + {17:d}]

# standalone
if __name__ == '__main__':
  import sys

  EXIT_SUCCESS = 0
  EXIT_FAILURE = 1

  if len(sys.argv) < 2:
    print(f'usage: {{sys.argv[0]:s}} x')
    print('x = gamma encoded intensity, calculates linear intensity')
    sys.exit(EXIT_FAILURE)
  x = float(sys.argv[1])

  y = gamma_decode_{18:s}(x)
  print(f'gamma encoded {{x:.6f}} -> linear {{y:.6f}}')'''.format(
    ','.join(
      [
        f'\n    {post_factor[i]:.16e}'
        for i in range(post_factor.shape[0])
      ]
    ),
    str(gamma_a),
    str(gamma_a),
    str(gamma_b),
    str(gamma_c),
    str(gamma_d),
    str(gamma_e),
    str(2. - gamma_c),
    str(2. - gamma_c),
    err,
    device,
    gamma_a * gamma_b,
    1. / gamma_a,
    gamma_c,
    exp1 + 1,
    p[-1],
    ''.join(
      [
        '  y = y * x {0:s} {1:.16e}\n'.format(
          '-' if p[i] < 0. else '+',
          abs(p[i])
        )
        for i in range(p.shape[0] - 2, -1, -1)
      ]
    ),
    -exp0,
    device
  )
)
