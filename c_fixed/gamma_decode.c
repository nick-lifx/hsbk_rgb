// generated by ../prepare/gamma_decode_gen_c_fixed.py

#include "gamma_decode.h"

static int32_t post_factor[] = {
  0x1bdb8d,
  0x93088c,
  0x3080c00,
  0x10000000,
  0x5472d14f
};

// argument and result in 2:30 fixed point
// returns approximation to:
//   x < 12.92f * .0031308f ? x / 12.92f : powf((x + .055f) / 1.055f, 2.4f)
// allowed domain (-inf, 1.945), recommended domain [-epsilon, 1 + epsilon]
// do not call with argument >= 1.945 due to table lookup overflow (unchecked)
// minimax error is up to 8.360671e-09 on domain [.445, .945]
int32_t gamma_decode(int32_t x) {
  if (x < 0x296bb54)
    return (int32_t)((x * 0x4f41c885LL + 0x200000000LL) >> 34);
  x += 0x3851eb8;
  int exp = 4;
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
  int32_t y = -0xcc27ee6;
  y = (int32_t)(((int64_t)y * x + 0x2767a3e61d6f1e00LL) >> 32);
  y = (int32_t)(((int64_t)y * x - 0x3af1b3344738cc00LL) >> 33);
  y = (int32_t)(((int64_t)y * x + 0x263605cb98310600LL) >> 31);
  y = (int32_t)(((int64_t)y * x + 0x1f0a83a297652e00LL) >> 31);
  y = (int32_t)(((int64_t)y * x - 0x2893cee49b735c0LL) >> 31);
  y = (int32_t)(((int64_t)y * x + 0x2cab80b9fbc3a0LL) >> 31);
  return (int32_t)(((int64_t)y * post_factor[exp] + 0x10000000LL) >> 29);
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

  int32_t y = gamma_decode(x);
  printf("gamma encoded %.6f -> linear %.6f\n", ldexpf(x, -30), ldexpf(y, -30));

  return EXIT_SUCCESS;
}
#endif
