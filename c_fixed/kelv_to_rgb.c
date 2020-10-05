// generated by ../prepare/kelv_to_rgb_gen_c_fixed.py

#include "gamma_encode.h"
#include "kelv_to_rgb.h"
#include "kelv_to_uv.h"

#define UV_u 0
#define UV_v 1
#define N_UV 2

#define UVL_U 0
#define UVL_V 1
#define UVL_L 2
#define N_UVL 3

#define RGB_RED 0
#define RGB_GREEN 1
#define RGB_BLUE 2
#define N_RGB 3

// this is precomputed for the particular primaries in use
int32_t UVL_to_rgb[N_RGB][N_UVL] = {
  {0x3e230c18, 0xb9e7d0f, -0xc1fd068},
  {-0x11edc530, 0x14482f55, 0x102ad55},
  {-0x5692c0d, -0x42bbc9f7, 0x19b3913e}
};

// kelv in 16:16 fixed point, results in 2:30 fixed point
void kelv_to_rgb(int32_t kelv, int32_t *rgb) {
  // find the approximate (u, v) chromaticity of the given Kelvin value
  int32_t uv[N_UV];
  kelv_to_uv(kelv, uv);

  // convert (u, v) to (R, G, B) in an optimized way
  // usually we would calculate w such that u + v + w = 1 and then take
  // (u, v, w) as (U, V, W) noting that brightness is arbitrary, and then
  // multiply through by a UVW -> rgb conversion matrix, but the matrix
  // used here expects L = U + V + W instead of W and L is always 1 here
  for (int i = 0; i < N_RGB; ++i)
    rgb[i] = (int32_t)(
      (
        (int64_t)uv[UV_u] * UVL_to_rgb[i][UVL_U] +
          (int64_t)uv[UV_v] * UVL_to_rgb[i][UVL_V] +
          (1 << 29)
      ) >> 30
    ) + UVL_to_rgb[i][UVL_L];

  // low Kelvins are outside the gamut of SRGB and thus must be interpreted,
  // in this simplistic approach we simply clip off the negative blue value
  for (int i = 0; i < N_RGB; ++i)
    if (rgb[i] < 0)
      rgb[i] = 0;

  // normalize the brightness, so that at least one of R, G, or B = 1
  int32_t max_rgb = rgb[RGB_RED];
  if (rgb[RGB_GREEN] > max_rgb)
    max_rgb = rgb[RGB_GREEN];
  if (rgb[RGB_BLUE] > max_rgb)
    max_rgb = rgb[RGB_BLUE];
  for (int i = 0; i < N_RGB; ++i)
    rgb[i] = (int32_t)((((int64_t)rgb[i] << 31) / max_rgb + 1) >> 1);

  // gamma-encode the R, G, B tuple according to the SRGB gamma curve
  // because displaying it on a monitor will gamma-decode it in the process
  for (int i = 0; i < N_RGB; ++i)
    rgb[i] = gamma_encode(rgb[i]);
}

#ifdef STANDALONE
#include <math.h>
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
  int32_t kelv = (int32_t)ldexpf(atof(argv[1]), 16);

  int32_t rgb[N_RGB];
  kelv_to_rgb(kelv, rgb);
  printf(
    "kelv %.3f -> RGB (%.6f, %.6f, %.6f)\n",
    ldexpf(kelv, -16),
    ldexpf(rgb[RGB_RED], -30),
    ldexpf(rgb[RGB_GREEN], -30),
    ldexpf(rgb[RGB_BLUE], -30)
  );

  return EXIT_SUCCESS;
}
#endif
