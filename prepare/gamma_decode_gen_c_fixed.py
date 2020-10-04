#!/usr/bin/env python3

import math
import numpy
import ruamel.yaml
import sys
from poly_fixed import poly_fixed
from python_to_numpy import python_to_numpy

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

EPSILON = 1e-8

if len(sys.argv) < 2:
  print(f'usage: {sys.argv[0]:s} gamma_decode_fit_in.yml [name]')
  sys.exit(EXIT_FAILURE)
gamma_decode_fit_in = sys.argv[1]
name = sys.argv[2] if len(sys.argv) >= 3 else 'gamma_decode'

yaml = ruamel.yaml.YAML(typ = 'safe')
#numpy.set_printoptions(threshold = numpy.inf)

with open(gamma_decode_fit_in) as fin:
  gamma_decode_fit = python_to_numpy(yaml.load(fin))
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

# final int64_t result will have exponent p_exp + post_factor_exp
# we want it to be -30, hence we will shift right by the difference
y_shr = -30 - p_exp - post_factor_exp

def to_hex(x):
  return '{0:s}0x{1:x}'.format('' if x >= 0 else '-', abs(x))
print(
  '''// generated by ../prepare/gamma_decode_gen_c_fixed.py

#include "gamma_decode.h"

static int32_t post_factor[] = {{{0:s}
}};

// argument and result in 2:30 fixed point
// returns approximation to:
//   x < 12.92f * .0031308f ? x / 12.92f : powf((x + .055f) / 1.055f, 2.4f)
// allowed domain [-2, 1.945), recommended domain [-epsilon, 1 + epsilon)
// minimax error is up to {1:e} on domain [.445, .945)
int32_t {2:s}(int32_t x) {{
  if (x < {3:s})
    return (int32_t)((x * {4:s}LL + {5:s}LL) >> {6:d});
  x += {7:s};
  int exp = {8:d};
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
  int32_t y = {9:s};
{10:s}  return (int32_t)(((int64_t)y * post_factor[exp] + {11:s}LL) >> {12:d});
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

  int32_t y = {13:s}(x);
  printf("gamma encoded %.6f -> linear %.6f\\n", ldexpf(x, -30), ldexpf(y, -30));

  return EXIT_SUCCESS;
}}
#endif'''.format(
    ','.join(
      [
        f'\n  {to_hex(post_factor[i]):s}'
        for i in range(post_factor.shape[0])
      ]
    ),
    err,
    name,
    to_hex(int(round(math.ldexp(12.92 * .0031308, 30)))),
    to_hex(int(round(math.ldexp(1. / 12.92, 34)))),
    to_hex(1 << 33),
    34,
    to_hex(int(round(math.ldexp(.055, 30)))),
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
    to_hex(1 << (y_shr - 1)),
    y_shr,
    name
  )
)
