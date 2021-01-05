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
#include "gamma_encode_srgb.h"
#include "uv_to_rgb.h"

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

void uv_to_rgb_convert(
  const struct uv_to_rgb *context,
  const float *uv,
  float *rgb
) {
  // validate inputs, allowing a little slack
  assert(uv[UV_u] >= -EPSILON && uv[UV_v] >= -EPSILON && uv[UV_u] + uv[UV_v] < 1.f + EPSILON);

  // convert (u, v) to (R, G, B) in an optimized way
  // usually we would calculate w such that u + v + w = 1 and then take
  // (u, v, w) as (U, V, W) noting that brightness is arbitrary, and then
  // multiply through by a UVW -> rgb conversion matrix, but the matrix
  // used here expects L = U + V + W instead of W and L is always 1 here
  for (int i = 0; i < N_RGB; ++i)
    rgb[i] =
      uv[UV_u] * context->UVL_to_rgb[i][UVL_U] +
      uv[UV_v] * context->UVL_to_rgb[i][UVL_V] +
      context->UVL_to_rgb[i][UVL_L];

  // low Kelvins are outside the gamut of SRGB and thus must be interpreted,
  // in this simplistic approach we simply clip off the negative blue value
  for (int i = 0; i < N_RGB; ++i)
    if (rgb[i] < 0.f)
      rgb[i] = 0.f;

  // normalize the brightness, so that at least one of R, G, or B = 1
  float max_rgb = rgb[RGB_RED];
  for (int i = RGB_GREEN; i < N_RGB; ++i)
    if (rgb[i] > max_rgb)
      max_rgb = rgb[i];
  for (int i = 0; i < N_RGB; ++i)
    rgb[i] /= max_rgb;

  // return gamma-encoded (R, G, B) tuple according to the SRGB gamma curve
  // because displaying it on a monitor will gamma-decode it in the process
  for (int i = 0; i < N_RGB; ++i)
    rgb[i] = context->gamma_encode(rgb[i]);
}

#ifdef STANDALONE
#include <stdlib.h>
#include <stdio.h>

void uv_to_rgb_standalone(
  const struct uv_to_rgb *uv_to_rgb,
  int argc,
  char **argv
) {
  if (argc < 3) {
    printf(
      "usage: %s u v\n"
        "u = CIE 1960 u coordinate (0 to 1)\n"
        "v = CIE 1960 v coordinate (0 to 1)\n"
        "sum of u and v cannot exceed 1\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }
  float uv[N_UV] = {atof(argv[1]), atof(argv[2])};

  float rgb[N_RGB];
  uv_to_rgb_convert(uv_to_rgb, uv, rgb);
  printf(
    "uv (%.6f, %.6f) -> RGB (%.6f, %.6f, %.6f)\n",
    uv[UV_u],
    uv[UV_v],
    rgb[RGB_RED],
    rgb[RGB_GREEN],
    rgb[RGB_BLUE]
  );
}
#endif
