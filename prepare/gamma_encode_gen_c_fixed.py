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

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

EPSILON = 1e-8

#numpy.set_printoptions(threshold = numpy.inf)

if len(sys.argv) < 3:
  print(f'usage: {sys.argv[0]:s} gamma_encode_fit_in.yml device')
  sys.exit(EXIT_FAILURE)
gamma_encode_fit_in = sys.argv[1]
device = sys.argv[2]

gamma_encode_fit = utils.yaml_io._import(
  utils.yaml_io.read_file(gamma_encode_fit_in)
)
gamma_a = gamma_encode_fit['gamma_a']
gamma_b = gamma_encode_fit['gamma_b']
gamma_c = gamma_encode_fit['gamma_c']
gamma_d = gamma_encode_fit['gamma_d']
gamma_e = gamma_encode_fit['gamma_e']
a = gamma_encode_fit['a']
b = gamma_encode_fit['b']
p = gamma_encode_fit['p']
err = gamma_encode_fit['err']
exp0 = gamma_encode_fit['exp0']
post_factor = gamma_encode_fit['post_factor']

p, p_shr, p_exp = poly_fixed(mpmath.matrix(p), a, b, -31, 31)

_, exp = numpy.frexp(post_factor * (1. + EPSILON))
post_factor_exp = numpy.max(exp) - 31
post_factor = (
  numpy.round(numpy.ldexp(post_factor, -post_factor_exp)).astype(numpy.int32)
)

# final int64_t result will have exponent p_exp + post_factor_exp
# we want it to be -30, hence we will shift right by the difference
y_shr = -30 - p_exp - post_factor_exp

def to_hex(x):
  return '{0:s}0x{1:x}'.format('' if x >= 0 else '-', abs(x))
print(
  '''// generated by ../prepare/gamma_encode_gen_c_fixed.py

// Copyright (c) 2020 Nick Downing
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to
// deal in the Software without restriction, including without limitation the
// rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
// sell copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
// IN THE SOFTWARE.

#include "gamma_encode_{0:s}.h"

static int32_t post_factor[] = {{{1:s}
}};

// argument and result in 2:30 fixed point
// returns approximation to:
//   x < {2:s}f ? x * {3:s}f : powf(x, 1.f / {4:s}f) * {5:s}f - {6:s}f
// allowed domain [-2, 2), recommended domain [-epsilon, 1 + epsilon)
// minimax error is up to {7:e} relative
int32_t gamma_encode_{8:s}(int32_t x) {{
  if (x < {9:s})
    return (int32_t)((x * {10:s}LL + {11:s}LL) >> {12:d});
  int exp = {13:d};
  if ((x & 0x7f800000) == 0) {{
    x <<= 8;
    exp -= 8;
  }}
  if ((x & 0x78000000) == 0) {{
    x <<= 4;
    exp -= 4;
  }}
  if ((x & 0x60000000) == 0) {{
    x <<= 2;
    exp -= 2;
  }}
  if ((x & 0x40000000) == 0) {{
    x <<= 1;
    exp -= 1;
  }}
  int32_t y = {14:s};
{15:s}  return (int32_t)(((int64_t)y * post_factor[exp] - {16:s}LL) >> {17:d});
}}

#ifdef STANDALONE
#include <math.h>
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv) {{
  if (argc < 2) {{
    printf(
      "usage: %s x\\n"
        "x = gamma encoded intensity, calculates linear intensity\\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }}
  int32_t x = (int32_t)roundf(ldexpf(atof(argv[1]), 30));

  int32_t y = gamma_encode_{18:s}(x);
  printf("gamma encoded %.6f -> linear %.6f\\n", ldexpf(x, -30), ldexpf(y, -30));

  return EXIT_SUCCESS;
}}
#endif'''.format(
    device,
    ','.join(
      [
        f'\n  {to_hex(post_factor[i]):s}'
        for i in range(post_factor.shape[0])
      ]
    ),
    str(gamma_b),
    str(gamma_a),
    str(gamma_e),
    str(gamma_d),
    str(gamma_c),
    err,
    device,
    to_hex(int(round(math.ldexp(gamma_b, 30)))),
    to_hex(int(round(math.ldexp(gamma_a, 27)))),
    to_hex(1 << 26),
    27,
    1 - exp0, # 2:30 argument has exponent -1 when viewed in 1:31 fixed point
    to_hex(p[-1]),
    ''.join(
      [
        '  y = (int32_t)(((int64_t)y * x {0:s} 0x{1:x}LL) >> {2:d});\n'.format(
          '-' if p[i] < 0. else '+',
          abs(p[i]),
          p_shr[i]
        )
        for i in range(p.shape[0] - 2, -1, -1)
      ]
    ),
    to_hex(
      int(round(math.ldexp(gamma_c, 30 + int(y_shr)))) - (1 << (y_shr - 1))
    ),
    y_shr,
    device
  )
)
