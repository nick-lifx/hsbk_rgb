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
#include "rgb_to_uv.h"

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

#define EPSILON (1 << 10)

void rgb_to_uv_convert(
  const struct rgb_to_uv *context,
  const int32_t *rgb,
  int32_t *uv
) {
  // validate inputs, allowing a little slack
  assert(rgb[RGB_RED] >= -EPSILON && rgb[RGB_RED] < (1 << 30) + EPSILON);
  assert(rgb[RGB_GREEN] >= -EPSILON && rgb[RGB_GREEN] < (1 << 30) + EPSILON);
  assert(rgb[RGB_BLUE] >= -EPSILON && rgb[RGB_BLUE] < (1 << 30) + EPSILON);
  assert((int64_t)rgb[RGB_RED] + rgb[RGB_GREEN] + rgb[RGB_BLUE] >= EPSILON);

  int32_t rgb1[N_RGB];
  for (int i = 0; i < N_RGB; ++i)
    rgb1[i] = context->gamma_decode(rgb[i]);

  int32_t UVL[N_UVL];
  for (int i = 0; i < N_UVL; ++i) {
    int64_t v = 1 << 29;
    for (int j = 0; j < N_RGB; ++j)
      v += (int64_t)context->rgb_to_UVL[i][j] * rgb1[j];
    UVL[i] = (int32_t)(v >> 30);
  }

  uv[UV_u] = (int32_t)((((int64_t)UVL[UVL_U] << 31) / UVL[UVL_L] + 1) >> 1);
  uv[UV_v] = (int32_t)((((int64_t)UVL[UVL_V] << 31) / UVL[UVL_L] + 1) >> 1);
}

#ifdef STANDALONE
#include <math.h>
#include <stdlib.h>
#include <stdio.h>

void rgb_to_uv_standalone(
  const struct rgb_to_uv *rgb_to_uv,
  int argc,
  char **argv
) {
  if (argc < 4) {
    printf(
      "usage: %s R G B\n"
        "R = red channel as fraction (0 to 1)\n"
        "G = green channel as fraction (0 to 1)\n"
        "B = blue channel as fraction (0 to 1)\n"
        "R, G and B cannot all be 0\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }
  int32_t rgb[N_RGB] = {
    (int32_t)roundf(ldexpf(atof(argv[1]), 30)),
    (int32_t)roundf(ldexpf(atof(argv[2]), 30)),
    (int32_t)roundf(ldexpf(atof(argv[3]), 30))
  };

  int32_t uv[N_UV];
  rgb_to_uv_convert(rgb_to_uv, rgb, uv);
  printf(
    "RGB (%.6f, %.6f, %.6f) -> uv (%.6f, %.6f)\n",
    ldexpf(rgb[RGB_RED], -30),
    ldexpf(rgb[RGB_GREEN], -30),
    ldexpf(rgb[RGB_BLUE], -30),
    ldexpf(uv[UV_u], -30),
    ldexpf(uv[UV_v], -30)
  );
}
#endif
