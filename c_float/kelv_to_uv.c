#include <assert.h>
#include "kelv_to_uv.h"

#define UV_u 0
#define UV_v 1
#define N_UV 2

#define EPSILON 1e-6

void kelv_to_uv(float kelv, float *uv) {
  // validate inputs, allowing a little slack
  assert(kelv >= 1000. - EPSILON && kelv < 15000. + EPSILON);

  // find the approximate (u, v) chromaticity of the given Kelvin value
  // see http://en.wikipedia.org/wiki/Planckian_locus#Approximation (Krystek)
  // we evaluate this with Horner's rule for better numerical stability
  uv[UV_u] =
    ((1.28641212e-7f * kelv + 1.54118254e-4f) * kelv + .860117757f) /
      ((7.08145163e-7f * kelv + 8.42420235e-4f) * kelv + 1.f);
  uv[UV_v] =
    ((4.20481691e-8f * kelv + 4.22806245e-5f) * kelv + .317398726f) /
      ((1.61456053e-7f * kelv - 2.89741816e-5f) * kelv + 1.f);
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
