#!/usr/bin/env python3

import numpy
import ruamel.yaml
import sys
from python_to_numpy import python_to_numpy

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

if len(sys.argv) < 2:
  print(f'usage: {sys.argv[0]:s} gamma_encode_fit_in.yml [name]')
  sys.exit(EXIT_FAILURE)
gamma_encode_fit_in = sys.argv[1]
name = sys.argv[2] if len(sys.argv) >= 3 else 'gamma_encode'

yaml = ruamel.yaml.YAML(typ = 'safe')
#numpy.set_printoptions(threshold = numpy.inf)

with open(gamma_encode_fit_in) as fin:
  gamma_encode_fit = python_to_numpy(yaml.load(fin))
p = gamma_encode_fit['p']
err = gamma_encode_fit['err']
exp0 = gamma_encode_fit['exp0']
post_factor = gamma_encode_fit['post_factor']

print(
  '''// generated by ../prepare/gamma_encode_gen_c_float.py

#include <math.h>
#include "gamma_encode.h"

static float post_factor[] = {{{0:s}
}};

// returns approximation to:
//   x < .0031308f ? x * 12.92f : powf(x, 1.f / 2.4f) * 1.055f - .055f
// allowed domain (-inf, 2), recommended domain [-epsilon, 1 + epsilon]
// do not call with argument >= 2 due to table lookup overflow (unchecked)
// minimax error is up to {1:e} on domain [.5, 1]
float {2:s}(float x) {{
  if (x < .0031308f)
    return x * 12.92f;
  int exp;
  x = frexpf(x, &exp);
  float y = {3:.8e}f;
{4:s}  return y * post_factor[exp + {5:d}] - .055f;
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

  float y = {6:s}(x);
  printf("linear %.6f -> gamma encoded %.6f\\n", x, y);

  return EXIT_SUCCESS;
}}
#endif'''.format(
    ','.join(
      [
        f'\n  {post_factor[i]:.8e}f'
        for i in range(post_factor.shape[0])
      ]
    ),
    err,
    name,
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
    name
  )
)