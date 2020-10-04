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

#define EPSILON 0x400

// ideally below would be [1, 1, 1] but unfortunately D65 whitepoint != 6504K
int32_t kelv_rgb_6504K[N_RGB] = {
  // old way (slower):
  // a hexadecimal version of what would be printed by
  //   ./kelv_to_rgb 6504
  //0x4000001e, 0x3e5729fe, 0x3fcc0d0c

  // new way (faster):
  // a hexadecimal version of what would be printed by
  //   ./mired_to_rgb 153.75154
  0x40000000, 0x3e77142b, 0x3fb975e6
};

// arguments in 2:30 fixed point
// results as follows:
//   hue in 0:32 fixed point
//   saturation in 2:30 fixed point
//   brightness in 2:30 fixed point
//   Kelvin in 16:16 fixed point
// all are signed, so the hue is taken to be in [180, 180), but
// if cast to unsigned then it would equivalently be in [0, 360)
void rgb_to_hsbk(const int32_t *rgb, int32_t kelv, int32_t *hsbk) {
  // validate inputs, allowing a little slack
  for (int i = 0; i < N_RGB; ++i)
    assert(rgb[i] >= -EPSILON && rgb[i] < (1 << 30) + EPSILON);

  // the Kelvin is always constant with this simplified algorithm
  // we will set the other values if we are able to calculate them
  memset(hsbk, 0, N_HSBK * sizeof(int32_t));
  int32_t kelv_rgb[3];
  if (kelv == 0) {
    hsbk[HSBK_KELV] = 6504 << 16;
    memcpy(kelv_rgb, kelv_rgb_6504K, N_RGB * sizeof(int32_t));
  }
  else {
    hsbk[HSBK_KELV] = kelv;

    // old way (slower):
    //kelv_to_rgb(kelv, kelv_rgb);

    // new way (faster):
    mired_to_rgb(
      (int32_t)(((1000000LL << 33) / kelv + 1) >> 1),
      kelv_rgb
    );
  }

  int32_t br = rgb[RGB_RED];
  if (rgb[RGB_GREEN] > br)
    br = rgb[RGB_GREEN];
  if (rgb[RGB_BLUE] > br)
    br = rgb[RGB_BLUE];
  if (br >= EPSILON) {
    // it is not fully black, so we can calculate saturation
    // note: do not corrupt the caller's value by doing rgb /= br
    hsbk[HSBK_BR] = br;
    int32_t rgb1[N_RGB];
    for (int i = 0; i < N_RGB; ++i)
      rgb1[i] = (int32_t)((((int64_t)rgb[i] << 31) / br + 1) >> 1);

    // subtract as much of kelv_rgb as we are able to without going negative
    // this will result in at least one of R, G, B = 0 (i.e. a limiting one)
    // we rely on the fact that kelv_factor[RGB_RED] cannot go below about .7
    int32_t kelv_factor = (int32_t)(
      (((int64_t)rgb1[RGB_RED] << 31) / kelv_rgb[RGB_RED] + 1) >> 1
    );
    int i = RGB_RED;
    if (
      rgb1[RGB_GREEN] < (int32_t)(
        ((int64_t)kelv_factor * kelv_rgb[RGB_GREEN] + (1 << 29)) >> 30
      )
    ) {
      kelv_factor = (int32_t)(
        (((int64_t)rgb1[RGB_GREEN] << 31) / kelv_rgb[RGB_GREEN] + 1) >> 1
      );
      i = RGB_GREEN;
    }
    if (
      rgb1[RGB_BLUE] < (int32_t)(
        ((int64_t)kelv_factor * kelv_rgb[RGB_BLUE] + (1 << 29)) >> 30
      )
    ) {
      kelv_factor = (int32_t)(
        (((int64_t)rgb1[RGB_BLUE] << 31) / kelv_rgb[RGB_BLUE] + 1) >> 1
      );
      i = RGB_BLUE;
    }
    int32_t hue_rgb[N_RGB];
    for (int j = 0; j < N_RGB; ++j)
      hue_rgb[j] = rgb1[j] - (int32_t)(
        ((int64_t)kelv_factor * kelv_rgb[j] + (1 << 29)) >> 30
      );
    assert(hue_rgb[i] < EPSILON);

    // at this point we can regenerate the original rgb by
    //   rgb = hue_rgb + kelv_factor * kelv_rgb
    // we will now scale up hue_rgb so that at least one of R, G, B = 1,
    // and record hue_factor to scale it down again to maintain the above
    int32_t hue_factor = hue_rgb[RGB_RED];
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
        hue_rgb[k] = (int32_t)(
          (((int64_t)hue_rgb[k] << 31) / hue_factor + 1) >> 1
        );

      // at this point we can regenerate the original rgb by
      //   rgb = hue_factor * hue_rgb + kelv_factor * kelv_rgb
      // if we now re-scale it so that hue_factor + kelv_factor == 1, then
      // hue_factor will be the saturation (sum will be approximately 1, it may
      // be larger, if hue_rgb and kelv_rgb are either side of the white point)
      hsbk[HSBK_SAT] = (int32_t)(
        (
           ((int64_t)hue_factor << 31) /
             ((int64_t)hue_factor + (int64_t)kelv_factor) +
               1
        ) >> 1
      );

      // at this point hue_rgb[i] == 0 and hue_rgb[j] == 1 and i != j
      // using the (i, j) we can resolve the hue down to a 60 degree segment,
      // then rgb[k] such that k != i and k != j tells us where in the segment
      hsbk[HSBK_HUE] = (int32_t)(
        (
          (
            i == 0 ?
              // no red (cyans)
              j == 1 ?
                // i = 0, j = 1 (more green): hue = 120 + 60 * rgb[2]
                (2LL << 30) + hue_rgb[RGB_BLUE] :
                // i = 0, j = 2 (more blue): hue = 240 - 60 * rgb[1]
                (-2LL << 30) - hue_rgb[RGB_GREEN] :
              i == 1 ?
                // no green (magentas)
                j == 0 ?
                  // i = 1, j = 0 (more red): hue = 360 - 60 * rgb[2]
                  (0LL << 30) - hue_rgb[RGB_BLUE] :
                  // i = 1, j = 2 (more blue): hue = 240 + 60 * rgb[0]
                  (-2LL << 30) + hue_rgb[RGB_RED] :
                // no blue (yellows)
                j == 0 ?
                  // i = 2, j = 0 (more red): hue = 0 + 60 * rgb[1]
                  (0LL << 30) + hue_rgb[RGB_GREEN] :
                  // i = 2, j = 1 (more green): hue = 120 - 60 * rgb[0]
                  (2LL << 30) - hue_rgb[RGB_RED]
          ) * (((1LL << 33) / 6 + 1) >> 1) + (1 << 29)
        ) >> 30
      );
    }
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
  int32_t rgb[N_RGB] = {
    (int32_t)roundf(ldexpf(atof(argv[1]), 30)),
    (int32_t)roundf(ldexpf(atof(argv[2]), 30)),
    (int32_t)roundf(ldexpf(atof(argv[3]), 30))
  };
  int32_t kelv =
    argc >= 5 ? (int32_t)roundf(ldexpf(atof(argv[4]), 16)) : (int32_t)0;

  int32_t hsbk[N_HSBK];
  rgb_to_hsbk(rgb, kelv, hsbk);
  printf(
    "RGB (%.6f, %.6f, %.6f) -> HSBK (%.3f, %.6f, %.6f, %.3f)\n",
    ldexpf(rgb[RGB_RED], -30),
    ldexpf(rgb[RGB_GREEN], -30),
    ldexpf(rgb[RGB_BLUE], -30),
    (uint32_t)hsbk[HSBK_HUE] * (float)(360. / (1LL << 32)),
    ldexpf(hsbk[HSBK_SAT], -30),
    ldexpf(hsbk[HSBK_BR], -30),
    ldexpf(hsbk[HSBK_KELV], -16)
  );

  return EXIT_SUCCESS;
}
#endif
