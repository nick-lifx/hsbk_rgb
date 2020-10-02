#include <math.h>
#include "kelv_to_rgb.h"
#include "kelv_to_uv.h"

#define UVW_U 0
#define UVW_V 1
#define UVW_W 2
#define N_UVW 3

#define RGB_RED 0
#define RGB_GREEN 1
#define RGB_BLUE 2
#define N_RGB 3

// this is precomputed for the particular primaries in use
float UVW_to_rgb[N_RGB][N_UVW] = {
  {12.5031573629705f, -0.126294518817885f, -3.0310684516292f},
  {-4.22958318635427f, 5.32310738384861f, 0.252614330742708f},
  {5.07265164410276f, -10.2580288802967f, 6.42535874919683f}
};

void kelv_to_rgb(float kelv, float *rgb) {
  // find the approximate (u, v) chromaticity of the given Kelvin value
  float UVW[N_UVW];
  kelv_to_uv(kelv, UVW);

  // add the missing w, to convert the chromaticity from (u, v) to (U, V, W)
  // see https://en.wikipedia.org/wiki/CIE_1960_color_space
  UVW[UVW_W] = 1.f - UVW[UVW_U] - UVW[UVW_V];

  // convert to rgb in the given system (the brightness will be arbitrary)
  for (int i = 0; i < N_RGB; ++i) {
    float v = 0.f;
    for (int j = 0; j < N_UVW; ++j)
      v += UVW_to_rgb[i][j] * UVW[j];
    rgb[i] = v;
  }

  // low Kelvins are outside the gamut of SRGB and thus must be interpreted,
  // in this simplistic approach we simply clip off the negative blue value
  for (int i = 0; i < N_RGB; ++i)
    if (rgb[i] < 0.f)
      rgb[i] = 0.f;

  // normalize the brightness, so that at least one of R, G, or B = 1
  float max_rgb = rgb[RGB_RED];
  if (rgb[RGB_GREEN] > max_rgb)
    max_rgb = rgb[RGB_GREEN];
  if (rgb[RGB_BLUE] > max_rgb)
    max_rgb = rgb[RGB_BLUE];
  for (int i = 0; i < N_RGB; ++i)
    rgb[i] /= max_rgb;

  // gamma-encode the R, G, B tuple according to the SRGB gamma curve
  // because displaying it on a monitor will gamma-decode it in the process
  for (int i = 0; i < N_RGB; ++i)
    rgb[i] =
      rgb[i] < .0031308 ?
        rgb[i] * 12.92f :
        1.055f * powf(rgb[i], 1.f / 2.4f) - .055f;
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

  float rgb[N_RGB];
  kelv_to_rgb(kelv, rgb);
  printf(
    "kelv %.3f -> RGB (%.6f, %.6f, %.6f)\n",
    kelv,
    rgb[RGB_RED],
    rgb[RGB_GREEN],
    rgb[RGB_BLUE]
  );

  return EXIT_SUCCESS;
}
#endif
