// generated by ../prepare/gamma_encode_gen_c_fixed.py

#include "gamma_encode.h"

static int32_t post_factor[] = {
  0x6597fa9,
  0x879c7c9,
  0xb504f33,
  0xf1a1bf4,
  0x1428a2fa,
  0x1ae89f99,
  0x23eb3588,
  0x2ff221af,
  0x40000000,
  0x556e0424
};

// argument and result in 2:30 fixed point
// returns approximation to:
//   x < .0031308f ? x * 12.92f : powf(x, 1.f / 2.4f) * 1.055f - .055f
// allowed domain (-inf, 2), recommended domain [-epsilon, 1 + epsilon]
// do not call with argument >= 2 due to table lookup overflow (unchecked)
// minimax error is up to 2.089029e-08 on domain [.5, 1]
int32_t gamma_encode(int32_t x) {
  if (x < 0x334b87)
    return (int32_t)((x * 0x675c28f6LL + 0x4000000LL) >> 27);
  int exp = 9;
  if ((x & 0x7f800000) == 0) {
    x <<= 8;
    exp -= 8;
  }
  if ((x & 0x78000000) == 0) {
    x <<= 4;
    exp -= 4;
  }
  if ((x & 0x60000000) == 0) {
    x <<= 2;
    exp -= 2;
  }
  if ((x & 0x40000000) == 0) {
    x <<= 1;
    exp -= 1;
  }
  int32_t y = 0x13da8964;
  y = (int32_t)(((int64_t)y * x - 0x3d003336ecfd2200LL) >> 33);
  y = (int32_t)(((int64_t)y * x + 0x29289c72913bc600LL) >> 32);
  y = (int32_t)(((int64_t)y * x - 0x2021a5dff59d0e00LL) >> 31);
  y = (int32_t)(((int64_t)y * x + 0x205e9166df8dbc00LL) >> 31);
  y = (int32_t)(((int64_t)y * x - 0x16d1800098157200LL) >> 30);
  y = (int32_t)(((int64_t)y * x + 0x1d7a5ac9dd8ea800LL) >> 30);
  y = (int32_t)(((int64_t)y * x + 0x8586a1c17e07600LL) >> 31);
  return (int32_t)(((int64_t)y * post_factor[exp] - 0xe147adf47ae148LL) >> 30);
}

#ifdef STANDALONE
#include <math.h>
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv) {
  if (argc < 2) {
    printf(
      "usage: %s x\n"
        "x = gamma encoded intensity, calculates linear intensity\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }
  int32_t x = (int32_t)roundf(ldexpf(atof(argv[1]), 30));

  int32_t y = gamma_encode(x);
  printf("gamma encoded %.6f -> linear %.6f\n", ldexpf(x, -30), ldexpf(y, -30));

  return EXIT_SUCCESS;
}
#endif
