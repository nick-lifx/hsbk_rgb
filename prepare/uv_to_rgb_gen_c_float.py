#!/usr/bin/env python3

# Copyright (c) 2020 Nick Downing
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import numpy
import ruamel.yaml
import sys
from python_to_numpy import python_to_numpy

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

if len(sys.argv) < 2:
  print(f'usage: {sys.argv[0]:s} primaries_in.yml [name]')
  sys.exit(EXIT_FAILURE)
primaries_in = sys.argv[1]
name = sys.argv[2] if len(sys.argv) >= 3 else 'uv_to_rgb'

yaml = ruamel.yaml.YAML(typ = 'safe')
#numpy.set_printoptions(threshold = numpy.inf)

with open(primaries_in) as fin:
  primaries = python_to_numpy(yaml.load(fin))
UVL_to_rgb = primaries['UVL_to_rgb']

print(
  '''// generated by ../prepare/uv_to_rgb_gen_c_float.py

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
#include "uv_to_rgb.h"
#include "gamma_encode.h"

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
float UVL_to_rgb[N_RGB][N_UVL] = {{
  {{{0:.8e}f, {1:.8e}f, {2:.8e}f}},
  {{{3:.8e}f, {4:.8e}f, {5:.8e}f}},
  {{{6:.8e}f, {7:.8e}f, {8:.8e}f}}
}};

#define EPSILON 1e-6f

void {9:s}(const float *uv, float *rgb) {{
  // validate inputs, allowing a little slack
  assert(uv[UV_u] >= -EPSILON && uv[UV_v] >= -EPSILON && uv[UV_u] + uv[UV_v] < 1.f + EPSILON); 

  // convert (u, v) to (R, G, B) in an optimized way
  // usually we would calculate w such that u + v + w = 1 and then take
  // (u, v, w) as (U, V, W) noting that brightness is arbitrary, and then
  // multiply through by a UVW -> rgb conversion matrix, but the matrix
  // used here expects L = U + V + W instead of W and L is always 1 here
  for (int i = 0; i < N_RGB; ++i)
    rgb[i] =
      uv[UV_u] * UVL_to_rgb[i][UVL_U] +
      uv[UV_v] * UVL_to_rgb[i][UVL_V] +
      UVL_to_rgb[i][UVL_L];

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

  // return gamma-encoded (R, G, B) tuple according to the SRGB gamma curve
  // because displaying it on a monitor will gamma-decode it in the process
  for (int i = 0; i < N_RGB; ++i)
    rgb[i] = gamma_encode(rgb[i]);
}}

#ifdef STANDALONE
#include <math.h>
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv) {{
  if (argc < 3) {{
    printf(
      "usage: %s u v\\n"
        "u = CIE 1960 u coordinate (0 to 1)\\n"
        "v = CIE 1960 v coordinate (0 to 1)\\n"
        "sum of u and v cannot exceed 1\\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }}
  float uv[N_UV] = {{atof(argv[1]), atof(argv[2])}};

  float rgb[N_RGB];
  {10:s}(uv, rgb);
  printf(
    "uv (%.6f, %.6f) -> RGB (%.6f, %.6f, %.6f)\\n",
    uv[UV_u],
    uv[UV_v],
    rgb[RGB_RED],
    rgb[RGB_GREEN],
    rgb[RGB_BLUE]
  );

  return EXIT_SUCCESS;
}}
#endif'''.format(
    UVL_to_rgb[0, 0],
    UVL_to_rgb[0, 1],
    UVL_to_rgb[0, 2],
    UVL_to_rgb[1, 0],
    UVL_to_rgb[1, 1],
    UVL_to_rgb[1, 2],
    UVL_to_rgb[2, 0],
    UVL_to_rgb[2, 1],
    UVL_to_rgb[2, 2],
    name,
    name
  )
)