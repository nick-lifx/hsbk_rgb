#!/usr/bin/env python3

import math

EPSILON = 1e-4

print(
  '''// generated by ../prepare/kelv_to_uv_gen_c_fixed.py

#include <assert.h>
#include <math.h>
#include "kelv_to_uv.h"

#define UV_u 0
#define UV_v 1
#define N_UV 2

// kelv in 16:16 fixed point, uv in 2:32 fixed point
void kelv_to_uv(int32_t kelv, int32_t *uv) {{
  // validate inputs, allowing a little slack
  assert(kelv >= 0x{0:x} && kelv < 0x{1:x});

  // find the approximate (u, v) chromaticity of the given Kelvin value
  // see http://en.wikipedia.org/wiki/Planckian_locus#Approximation (Krystek)
  // we evaluate this with Horner's rule for better numerical stability
  int32_t u = 0x{2:x};
  u = (int32_t)(((int64_t)u * kelv + 0x{3:x}LL) >> 26);
  u = (int32_t)(((int64_t)u * kelv + 0x{4:x}LL) >> 26);
  int32_t u_denom = 0x{5:x};
  u_denom = (int32_t)(((int64_t)u_denom * kelv + 0x{6:x}LL) >> 26);
  u_denom = (int32_t)(((int64_t)u_denom * kelv + 0x{7:x}LL) >> 26);
  uv[UV_u] = (int32_t)((((int64_t)u << 31) / u_denom + 1) >> 1);

  int32_t v = 0x{8:x};
  v = (int32_t)(((int64_t)v * kelv + 0x{9:x}LL) >> 26);
  v = (int32_t)(((int64_t)v * kelv + 0x{10:x}LL) >> 26);
  int32_t v_denom = 0x{11:x};
  v_denom = (int32_t)(((int64_t)v_denom * kelv - 0x{12:x}LL) >> 26);
  v_denom = (int32_t)(((int64_t)v_denom * kelv + 0x{13:x}LL) >> 26);
  uv[UV_v] = (int32_t)((((int64_t)v << 31) / v_denom + 1) >> 1);
}}

#ifdef STANDALONE
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv) {{
  if (argc < 2) {{
    printf(
      "usage: %s kelv\\n"
        "kelv = colour temperature in degrees Kelvin\\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }}
  int32_t kelv = (int32_t)roundf(ldexpf(atof(argv[1]), 16));

  int32_t uv[N_UV];
  kelv_to_uv(kelv, uv);
  printf(
    "kelv %.3f -> uv (%.6f, %.6f)\\n",
    ldexpf(kelv, -16),
    ldexpf(uv[UV_u], -30),
    ldexpf(uv[UV_v], -30)
  );

  return EXIT_SUCCESS;
}}
#endif
'''.format(
    int(round(math.ldexp(1000. - EPSILON, 16))),
    int(round(math.ldexp(15000. + EPSILON, 16))),
    int(round(math.ldexp(1.28641212e-7, 40))),
    int(round(math.ldexp(1.54118254e-4, 30 + 26))) + (1 << 25),
    int(round(math.ldexp(.860117757, 20 + 26))) + (1 << 25),
    int(round(math.ldexp(7.08145163e-7, 40))),
    int(round(math.ldexp(8.42420235e-4, 30 + 26))) + (1 << 25),
    int(round(math.ldexp(1., 20 + 26))) + (1 << 25),
    int(round(math.ldexp(4.20481691e-8, 40))),
    int(round(math.ldexp(4.22806245e-5, 30 + 26))) + (1 << 25),
    int(round(math.ldexp(.317398726, 20 + 26))) + (1 << 25),
    int(round(math.ldexp(1.61456053e-7, 40))),
    int(round(math.ldexp(2.89741816e-5, 30 + 26))) - (1 << 25),
    int(round(math.ldexp(1., 20 + 26))) + (1 << 25)
  )
)
