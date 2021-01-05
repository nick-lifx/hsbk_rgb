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

#define EPSILON 1e-6f

void rgb_to_uv_convert(
  const struct rgb_to_uv *context,
  const float *rgb,
  float *uv
) {
  // validate inputs, allowing a little slack
  assert(rgb[RGB_RED] >= -EPSILON && rgb[RGB_RED] < 1.f + EPSILON);
  assert(rgb[RGB_GREEN] >= -EPSILON && rgb[RGB_GREEN] < 1.f + EPSILON);
  assert(rgb[RGB_BLUE] >= -EPSILON && rgb[RGB_BLUE] < 1.f + EPSILON);
  assert(rgb[RGB_RED] + rgb[RGB_GREEN] + rgb[RGB_BLUE] >= EPSILON);

  float rgb1[N_RGB];
  for (int i = 0; i < N_RGB; ++i)
    rgb1[i] = context->gamma_decode(rgb[i]);

  float UVL[N_UVL];
  for (int i = 0; i < N_UVL; ++i) {
    float v = 0.f;
    for (int j = 0; j < N_RGB; ++j)
      v += context->rgb_to_UVL[i][j] * rgb1[j];
    UVL[i] = v;
  }

  uv[UV_u] = UVL[UVL_U] / UVL[UVL_L];
  uv[UV_v] = UVL[UVL_V] / UVL[UVL_L];
}

#ifdef STANDALONE
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
  float rgb[N_RGB] = {atof(argv[1]), atof(argv[2]), atof(argv[3])};

  float uv[N_UV];
  rgb_to_uv_convert(rgb_to_uv, rgb, uv);
  printf(
    "RGB (%.6f, %.6f, %.6f) -> uv (%.6f, %.6f)\n",
    rgb[RGB_RED],
    rgb[RGB_GREEN],
    rgb[RGB_BLUE],
    uv[UV_u],
    uv[UV_v]
  );
}
#endif
