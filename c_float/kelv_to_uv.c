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
#include "kelv_to_uv.h"

#define UV_u 0
#define UV_v 1
#define N_UV 2

#define EPSILON 1e-6f

void kelv_to_uv(float kelv, float *uv) {
  // validate inputs, allowing a little slack
  assert(kelv >= 1000.f * (1.f - EPSILON) && kelv < 15000. * (1.f + EPSILON));

  // find the approximate (u, v) chromaticity of the given Kelvin value
  // see http://en.wikipedia.org/wiki/Planckian_locus#Approximation (Krystek)
  // we evaluate this with Horner's rule for better numerical stability
  float u = 1.28641212e-7f;
  u = u * kelv + 1.54118254e-4f;
  u = u * kelv + .860117757f;
  float u_denom = 7.08145163e-7f;
  u_denom = u_denom * kelv + 8.42420235e-4f;
  u_denom = u_denom * kelv + 1.f;
  uv[UV_u] = u / u_denom;

  float v = 4.20481691e-8f;
  v = v * kelv + 4.22806245e-5f;
  v = v * kelv + .317398726f;
  float v_denom = 1.61456053e-7f;
  v_denom = v_denom * kelv - 2.89741816e-5f;
  v_denom = v_denom * kelv + 1.f;
  uv[UV_v] = v / v_denom;
}

#ifdef STANDALONE
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv) {
  if (argc < 2) {
    printf(
      "usage: %s kelv\n"
        "kelv = colour temperature in degrees Kelvin\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }
  float kelv = atof(argv[1]);

  float uv[N_UV];
  kelv_to_uv(kelv, uv);
  printf(
    "kelv %.3f -> uv (%.6f, %.6f)\n",
    kelv,
    uv[UV_u],
    uv[UV_v]
  );

  return EXIT_SUCCESS;
}
#endif
