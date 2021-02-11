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

import math
import mpmath
import numpy
import utils.yaml_io
from utils.poly_fixed import poly_fixed
from utils.to_fixed import to_fixed
from utils.to_hex import to_hex

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

EPSILON = 1e-8

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
a = gamma_decode_fit['a']
b = gamma_decode_fit['b']
p = gamma_decode_fit['p']
err = gamma_decode_fit['err']
exp0 = gamma_decode_fit['exp0']
post_factor = gamma_decode_fit['post_factor']

p, p_shr, p_exp = poly_fixed(p, a, b, -31, 31)

_, exp = numpy.frexp(post_factor * (1. + EPSILON))
post_factor_exp = numpy.max(exp) - 31
post_factor = (
  numpy.round(numpy.ldexp(post_factor, -post_factor_exp)).astype(numpy.int32)
)

# final int64_t result will have exponent p_exp[0] + post_factor_exp
# we want it to be -30, hence we will shift right by the difference
y_shr = -30 - p_exp[0] - post_factor_exp

sys.stdout.write(
  sys.stdin.read().format(
    device = device,
    post_factor = ','.join(
      [
        f'\n  {to_hex(post_factor[i]):s}'
        for i in range(post_factor.shape[0])
      ]
    ),
    str_gamma_a = str(gamma_a),
    str_gamma_b = str(gamma_b),
    str_gamma_c = str(gamma_c),
    str_gamma_d = str(gamma_d),
    str_gamma_e = str(gamma_e),
    two_minus_gamma_c = str(2. - gamma_c),
    err = err,
    gamma_a_gamma_b = to_fixed(gamma_a * gamma_b, -30),
    gamma_a_recip = to_fixed(1. / gamma_a, -34),
    gamma_a_recip_half = to_hex(1 << 33),
    gamma_a_recip_shr = 34,
    gamma_c = to_fixed(gamma_c, -30),
    one_minus_exp0 = 1 - exp0, # 2:30 argument has exponent -1 when viewed in 1:31 fixed point
    p_last = to_hex(p[-1]),
    p = ''.join(
      [
        '  y = (int32_t)(((int64_t)y * x {0:s} {1:s}LL) >> {2:d});\n'.format(
          '-' if p[i] < 0. else '+',
          to_hex(abs(p[i])),
          p_shr[i]
        )
        for i in range(p.shape[0] - 2, -1, -1)
      ]
    ),
    y_half = to_hex(1 << (y_shr - 1)),
    y_shr = y_shr
  )
)
