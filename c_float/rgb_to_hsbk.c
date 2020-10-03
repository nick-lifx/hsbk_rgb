#include <assert.h>
#include <math.h>
#include <string.h>
#include "rgb_to_hsbk.h"

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

#define EPSILON 1e-6f

// table for looking up hues when rgb[i] == 0 and rgb[j] == 1
struct hue_table {
  float hue_base;
  float hue_delta;
  int channel;
} hue_table[N_RGB][N_RGB] = {
  // no red (cyans)
  {
    {  0.f,   0.f, 0}, // not used
    {120.f,  60.f, 2}, // i = 0, j = 1 (more green): hue = 120 + 60 * rgb[2]
    {240.f, -60.f, 1}  // i = 0, j = 2 (more blue): hue = 240 - 60 * rgb[1]
  },
  // no green (magentas)
  {
    {360.f, -60.f, 2}, // i = 1, j = 0 (more red): hue = 360 - 60 * rgb[2]
    {  0.f,   0.f, 0}, // not used
    {240.f,  60.f, 0}  // i = 1, j = 2 (more blue): hue = 240 + 60 * rgb[0]
  },
  // no blue (yellows)
  {
    {  0.f,  60.f, 1}, // i = 2, j = 0 (more red): hue = 0 + 60 * rgb[1]
    {120.f, -60.f, 0}, // i = 2, j = 1 (more green): hue = 120 - 60 * rgb[0]
    {  0.f,   0.f, 0}  // not used
  }
};

// ideally below would be [1, 1, 1] but unfortunately D65 whitepoint != 6504K
float kelv_rgb_6504K[N_RGB] = {
  // old way (slower):
  // a more accurate version of what would be printed by
  //   ./kelv_to_rgb 6504
  //1.000000000000000, 0.974069550996864, 0.996829660936723

  // new way (faster):
  // a more accurate version of what would be printed by
  //   ./mired_to_rgb 153.751537515375
  1.000000000000000, 0.976013921677787, 0.995894521802491
};

void rgb_to_hsbk(const float *rgb, float kelv, float *hsbk) {
  // validate inputs, allowing a little slack
  for (int i = 0; i < N_RGB; ++i)
    assert(rgb[i] >= -EPSILON && rgb[i] < 1.f + EPSILON);

  // the Kelvin is always constant with this simplified algorithm
  // we will set the other values if we are able to calculate them
  memset(hsbk, 0, N_HSBK * sizeof(float));
  hsbk[HSBK_KELV] = 6504.f;
  float kelv_rgb[3];
  memcpy(kelv_rgb, kelv_rgb_6504K, N_RGB * sizeof(float));

  if (kelv) {
    hsbk[HSBK_KELV] = kelv;

    // old way (slower):
    //kelv_to_rgb(kelv, kelv_rgb);

    // new way (faster):
    mired_to_rgb(1e6f / kelv, kelv_rgb);
  }

  float br = rgb[RGB_RED];
  if (rgb[RGB_GREEN] > br)
    br = rgb[RGB_GREEN];
  if (rgb[RGB_BLUE] > br)
    br = rgb[RGB_BLUE];
  if (br >= EPSILON) {
    // it is not fully black, so we can calculate saturation
    // note: do not corrupt the caller's value by doing rgb /= br
    float rgb1[N_RGB];
    for (int i = 0; i < N_RGB; ++i)
      rgb1[i] = rgb[i] / br;

    // subtract as much of kelv_rgb as we are able to without going negative
    // this will result in at least one of R, G, B = 0 (i.e. a limiting one)
    float kelv_factor = rgb1[RGB_RED] / kelv_rgb[RGB_RED];
    int i = RGB_RED;
    float kelv_factor1 = rgb1[RGB_GREEN] / kelv_rgb[RGB_GREEN];
    if (kelv_factor1 < kelv_factor) {
      kelv_factor = kelv_factor1;
      i = RGB_GREEN;
    }
    float kelv_factor2 = rgb1[RGB_BLUE] / kelv_rgb[RGB_BLUE];
    if (kelv_factor2 < kelv_factor) {
      kelv_factor = kelv_factor2;
      i = RGB_BLUE;
    }
    float hue_rgb[N_RGB];
    for (int j = 0; j < N_RGB; ++j)
      hue_rgb[j] = rgb1[j] - kelv_factor * kelv_rgb[j];
    assert(hue_rgb[i] < EPSILON);

    // at this point we can regenerate the original rgb by
    //   rgb = hue_rgb + kelv_factor * kelv_rgb
    // we will now scale up hue_rgb so that at least one of R, G, B = 1,
    // and record hue_factor to scale it down again to maintain the above
    float hue_factor = hue_rgb[RGB_RED];
    int j = RGB_RED;
    if (hue_rgb[RGB_GREEN] > hue_factor) {
      hue_factor = hue_rgb[RGB_GREEN];
      j = RGB_GREEN;
    }
    if (hue_rgb[RGB_BLUE] > hue_factor) {
      hue_factor = hue_rgb[RGB_BLUE];
      j = RGB_BLUE;
    }
    if (hue_factor >= EPSILON) {
      // it is not fully white, so we can calculate hue
      assert(j != i); // we know hue_rgb[i] < EPSILON, hue_rgb[j] >= EPSILON
      for (int k = 0; k < N_RGB; ++k)
        hue_rgb[k] /= hue_factor;

      // at this point we can regenerate the original rgb by
      //   rgb = hue_factor * hue_rgb + kelv_factor * kelv_rgb
      // if we now re-scale it so that hue_factor + kelv_factor == 1, then
      // hue_factor will be the saturation (sum will be approximately 1, it may
      // be larger, if hue_rgb and kelv_rgb are either side of the white point)
      float sat = hue_factor / (hue_factor + kelv_factor);

      // at this point hue_rgb[i] == 0 and hue_rgb[j] == 1 and i != j
      // using the (i, j) we can resolve the hue down to a 60 degree segment,
      // then rgb[k] such that k != i and k != j tells us where in the segment
      struct hue_table ht = hue_table[i][j];
      float hue = ht.hue_base + ht.hue_delta * hue_rgb[ht.channel];

      hsbk[HSBK_HUE] = hue;
      hsbk[HSBK_SAT] = sat;
    }

    hsbk[HSBK_BR] = br;
  }
}

#ifdef STANDALONE
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv) {
  if (argc < 4) {
    printf(
      "usage: %s R G B [kelv]\n"
        "R = red channel as fraction (0 to 1)\n"
        "G = green channel as fraction (0 to 1)\n"
        "B = blue channel as fraction (0 to 1)\n"
        "kelv = white point to use in conversion (in degrees Kelvin; default 6504K)\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }
  float rgb[N_RGB] = {atof(argv[1]), atof(argv[2]), atof(argv[3])};
  float kelv = argc >= 5 ? atof(argv[4]) : 6504.f;

  float hsbk[N_HSBK];
  rgb_to_hsbk(rgb, kelv, hsbk);
  printf(
    "RGB (%.6f, %.6f, %.6f) -> HSBK (%.3f, %.6f, %.6f, %.3f)\n",
    rgb[RGB_RED],
    rgb[RGB_GREEN],
    rgb[RGB_BLUE],
    hsbk[HSBK_HUE],
    hsbk[HSBK_SAT],
    hsbk[HSBK_BR],
    hsbk[HSBK_KELV]
  );

  return EXIT_SUCCESS;
}
#endif
