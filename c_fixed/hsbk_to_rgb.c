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

#define EPSILON0 0x400
#define EPSILON1 0x40

// arguments as follows:
//   hue in 0:32 fixed point
//   saturation in 2:30 fixed point
//   brightness in 2:30 fixed point
//   Kelvin in 16:16 fixed point
// results in 2:30 fixed point
// all are signed, so the hue is taken to be in [180, 180), but
// if cast to unsigned then it would equivalently be in [0, 360)
void hsbk_to_rgb(const int32_t *hsbk, int32_t *rgb) {
  // validate inputs, allowing a little slack
  // the hue does not matter as it will be normalized modulo 360
  int64_t hue = hsbk[HSBK_HUE];
  int32_t sat = hsbk[HSBK_SAT];
  assert(sat >= -EPSILON0 && sat < (1 << 30) + EPSILON0);
  int64_t br = hsbk[HSBK_BR];
  assert(br >= -EPSILON0 && br < (1 << 30) + EPSILON0);
  int32_t kelv = hsbk[HSBK_KELV];
  assert(kelv >= (1500 << 16) - EPSILON1 && kelv < (9000 << 16) + EPSILON1);

  // this section computes hue_rgb from hue

  // put it in the form hue = (i + j) * 60 where i is integer, j is fraction
  hue = hue * 6 + 2;
  int i = (int)(hue >> 32); // in [-3, 3)
  int32_t j = (int32_t)((uint32_t)hue >> 2); // in [0, 0x40000000)

  // interpolate
  // interpolation is done in gamma-encoded space, as Photoshop HSV does it
  // the result of this interpolation will have at least one of R, G, B = 1
  int32_t hue_rgb[N_RGB];
  switch (i) {
  case -3: // [180, 240) cyan->blue
    hue_rgb[RGB_RED] = 0;
    hue_rgb[RGB_GREEN] = (1 << 30) - j;
    hue_rgb[RGB_BLUE] = 1 << 30;
    break;
  case -2: // [240, 300) blue->magenta
    hue_rgb[RGB_RED] = j;
    hue_rgb[RGB_GREEN] = 0;
    hue_rgb[RGB_BLUE] = 1 << 30;
    break;
  case -1: // [300, 360) magenta->red
    hue_rgb[RGB_RED] = 1 << 30;
    hue_rgb[RGB_GREEN] = 0;
    hue_rgb[RGB_BLUE] = (1 << 30) - j;
    break;
  case 0: // [0, 60) red->yellow
    hue_rgb[RGB_RED] = 1 << 30;
    hue_rgb[RGB_GREEN] = j;
    hue_rgb[RGB_BLUE] = 0;
    break;
  case 1: // [60, 120) yellow->green
    hue_rgb[RGB_RED] = (1 << 30) - j;
    hue_rgb[RGB_GREEN] = 1 << 30;
    hue_rgb[RGB_BLUE] = 0;
    break;
  case 2: // [120, 180) green->cyan
    hue_rgb[RGB_RED] = 0;
    hue_rgb[RGB_GREEN] = 1 << 30;
    hue_rgb[RGB_BLUE] = j;
    break;
  }

  // this section computes kelv_rgb from kelv

  int32_t kelv_rgb[N_RGB];

  // old way (slower):
  //kelv_to_rgb(kelv, kelv_rgb);

  // new way (faster):
  mired_to_rgb(
    (int32_t)(((1000000LL << 33) / kelv + 1) >> 1),
    kelv_rgb
  );

  // this section applies the saturation

  // do the mixing in gamma-encoded RGB space
  // this is not very principled and can corrupt the chromaticities
  for (int k = 0; k < N_RGB; ++k)
    rgb[k] = kelv_rgb[k] + (int32_t)(
      ((int64_t)sat * (hue_rgb[k] - kelv_rgb[k]) + (1 << 29)) >> 30
    );

  // normalize the brightness again
  // this is needed because SRGB produces the brightest colours near the white
  // point, so if hue_rgb and kelv_rgb are on opposite sides of the white point,
  // then rgb could land near the white point, but not be as bright as possible
  int32_t max_rgb = rgb[RGB_RED];
  if (rgb[RGB_GREEN] > max_rgb)
    max_rgb = rgb[RGB_GREEN];
  if (rgb[RGB_BLUE] > max_rgb)
    max_rgb = rgb[RGB_BLUE];

  // the minimum of max_rgb would be .5 and is reached when saturation is .5,
  // this would leave br = 2 + epsilon, hence we declared br as int64_t above
  br = (((br << 31) / max_rgb) + 1) >> 1;

  // this section applies the brightness

  // do the scaling in gamma-encoded RGB space
  // this is not very principled and can corrupt the chromaticities
  for (int i = 0; i < N_RGB; ++i)
    rgb[i] = (int32_t)((rgb[i] * br + (1 << 29)) >> 30);
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
  int32_t hsbk[N_HSBK] = {
    (int32_t)(int64_t)roundf(atof(argv[1]) * (float)((1LL << 32) / 360.)),
    (int32_t)roundf(ldexpf(atof(argv[2]), 30)),
    (int32_t)roundf(ldexpf(atof(argv[3]), 30)),
    argc >= 5 ?
      (int32_t)roundf(ldexpf(atof(argv[4]), 16)) :
      (int32_t)6504 << 16
  };

  int32_t rgb[N_RGB];
  hsbk_to_rgb(hsbk, rgb);
  printf(
    "HSBK (%.3f, %.6f, %.6f, %.3f) -> RGB (%.6f, %.6f, %.6f)\n",
    (uint32_t)hsbk[HSBK_HUE] * (float)(360. / (1LL << 32)),
    ldexpf(hsbk[HSBK_SAT], -30),
    ldexpf(hsbk[HSBK_BR], -30),
    ldexpf(hsbk[HSBK_KELV], -16),
    ldexpf(rgb[RGB_RED], -30),
    ldexpf(rgb[RGB_GREEN], -30),
    ldexpf(rgb[RGB_BLUE], -30)
  );

  return EXIT_SUCCESS;
}
#endif
