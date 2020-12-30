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

import numpy
import utils.yaml_io

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

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
p = gamma_encode_fit['p']
err = gamma_encode_fit['err']
exp0 = gamma_encode_fit['exp0']
exp1 = gamma_encode_fit['exp1']
post_factor = gamma_encode_fit['post_factor']

print(
  '''// generated by ../prepare/gamma_encode_gen_c_float.py

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

#include <assert.h>
#include <math.h>
#include "gamma_encode_{0:s}.h"

static float post_factor[] = {{{1:s}
}};

// returns approximation to:
//   x < {2:s}f ? x * {3:s}f : powf(x, 1.f / {4:s}f) * {5:s}f - {6:s}f
// allowed domain (-inf, 2), recommended domain [-epsilon, 1 + epsilon)
// do not call with argument >= 2 due to table lookup overflow (unchecked)
// minimax error is up to {7:e} relative
float gamma_encode_{8:s}(float x) {{
  if (x < {9:.8e}f)
    return x * {10:.8e}f;
  int exp;
  x = frexpf(x, &exp);
  assert(exp < {11:d});
  float y = {12:.8e}f;
{13:s}  return y * post_factor[exp + {14:d}] - {15:.8e}f;
}}

#ifdef STANDALONE
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv) {{
  if (argc < 2) {{
    printf(
      "usage: %s x\\n"
        "x = linear intensity, calculates gamma encoded intensity\\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }}
  float x = atof(argv[1]);

  float y = gamma_encode_{16:s}(x);
  printf("linear %.6f -> gamma encoded %.6f\\n", x, y);

  return EXIT_SUCCESS;
}}
#endif'''.format(
    device,
    ','.join(
      [
        f'\n  {post_factor[i]:.8e}f'
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
    gamma_b,
    gamma_a,
    exp1 + 1,
    p[-1],
    ''.join(
      [
        '  y = y * x {0:s} {1:.8e}f;\n'.format(
          '-' if p[i] < 0. else '+',
          abs(p[i])
        )
        for i in range(p.shape[0] - 2, -1, -1)
      ]
    ),
    -exp0,
    gamma_c,
    device
  )
)
