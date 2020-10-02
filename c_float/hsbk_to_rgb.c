#include <assert.h>
#include <math.h>
#include "hsbk_to_rgb.h"

// old way (slower):
//#include "kelv_to_rgb.h"

// new way (faster):
#include "mired_to_rgb.h"

#define RGB_RED 0
#define RGB_GREEN 1
#define RGB_BLUE 2
#define N_RGB 3

#define HSBK_HUE 0
#define HSBK_SAT 1
#define HSBK_BR 2
#define HSBK_KELV 3
#define N_HSBK 4

// define hues as red->yellow->green->cyan->blue->magenta->red again
// across is hue 0, 60, 120, 180, 240, 300, 360, down is R, G, B
// for interpolation, e.g. hue of 10 = column 1 + 10/60 * (column 2 - column 1)
#define N_HUE_SEQUENCE 6
float hue_sequence[N_RGB][N_HUE_SEQUENCE + 1] = {
  {1.f, 1.f, 0.f, 0.f, 0.f, 1.f, 1.f},
  {0.f, 1.f, 1.f, 1.f, 0.f, 0.f, 0.f},
  {0.f, 0.f, 0.f, 1.f, 1.f, 1.f, 0.f}
};

#define EPSILON 1e-6

void hsbk_to_rgb(const float *hsbk, float *rgb) {
  // validate inputs, allowing a little slack
  // the hue does not matter as it will be normalized modulo 360
  float hue = hsbk[HSBK_HUE];
  float sat = hsbk[HSBK_SAT];
  assert(sat >= -EPSILON && sat < 1. + EPSILON);
  float br = hsbk[HSBK_BR];
  assert(br >= -EPSILON && br < 1. + EPSILON);
  float kelv = hsbk[HSBK_KELV];
  assert(kelv >= 1500. - EPSILON && kelv < 9000. + EPSILON);

  // this section computes hue_rgb from hue

  // put it in the form hue = (i + j) * 60 where i is integer, j is fraction
  hue /= 60.f;
  int i = (int)floorf(hue);
  float j = hue - i;
  i %= 6;
  if (i < 0)
    i += 6;

  // interpolate from the table
  // interpolation is done in gamma-encoded space, as Photoshop HSV does it
  // the result of this interpolation will have at least one of R, G, B = 1
  float hue_rgb[N_RGB];
  for (int k = 0; k < N_RGB; ++k)
    hue_rgb[k] = 
      hue_sequence[k][i] +
        j * (hue_sequence[k][i + 1] - hue_sequence[k][i]);

  // this section computes kelv_rgb from kelv

  float kelv_rgb[N_RGB];

  // old way (slower):
  //kelv_to_rgb(kelv, kelv_rgb);

  // new way (faster):
  mired_to_rgb(1e6f / kelv, kelv_rgb);

  // this section applies the saturation

  // do the mixing in gamma-encoded RGB space
  // this is not very principled and can corrupt the chromaticities
  for (int k = 0; k < N_RGB; ++k)
    rgb[k] = kelv_rgb[k] + sat * (hue_rgb[k] - kelv_rgb[k]);

  // normalize the brightness again
  // this is needed because SRGB produces the brightest colours near the white
  // point, so if hue_rgb and kelv_rgb are on opposite sides of the white point,
  // then rgb could land near the white point, but not be as bright as possible
  float max_rgb = rgb[RGB_RED];
  if (rgb[RGB_GREEN] > max_rgb)
    max_rgb = rgb[RGB_GREEN];
  if (rgb[RGB_BLUE] > max_rgb)
    max_rgb = rgb[RGB_BLUE];
  br /= max_rgb;

  // this section applies the brightness

  // do the scaling in gamma-encoded RGB space
  // this is not very principled and can corrupt the chromaticities
  for (int i = 0; i < N_RGB; ++i)
    rgb[i] *= br;
}

#ifdef STANDALONE
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv) {
  if (argc < 4) {
    printf(
      "usage: %s hue sat br [kelv]\n"
        "hue = hue in degrees (0 to 360)\n"
        "sat = saturation as fraction (0 to 1)\n"
        "br = brightness as fraction (0 to 1)\n"
        "kelv = white point in degrees Kelvin (defaults to 6504K)\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }
  float hsbk[N_HSBK] = {
    atof(argv[1]),
    atof(argv[2]),
    atof(argv[3]),
    argc >= 5 ? atof(argv[4]) : 6504.f
  };

  float rgb[N_RGB];
  hsbk_to_rgb(hsbk, rgb);
  printf(
    "HSBK (%.3f, %.6f, %.6f, %.3f) -> RGB (%.6f, %.6f, %.6f)\n",
    hsbk[HSBK_HUE],
    hsbk[HSBK_SAT],
    hsbk[HSBK_BR],
    hsbk[HSBK_KELV],
    rgb[RGB_RED],
    rgb[RGB_GREEN],
    rgb[RGB_BLUE]
  );

  return EXIT_SUCCESS;
}
#endif
