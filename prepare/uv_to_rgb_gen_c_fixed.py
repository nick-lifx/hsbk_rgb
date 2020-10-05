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

import math
import numpy
import ruamel.yaml
import sys
from python_to_numpy import python_to_numpy

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

EPSILON = 1e-8

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
UVW_to_rgb = primaries['UVW_to_rgb']

# choose precision so that we can store the matrix and also the extreme values
# of the conversion result, which are at (u, v) = (0, 0), (1, 0) and (1, 1)
_, exp = numpy.frexp(
  UVL_to_rgb @ numpy.array(
    [
      [1., 0., 0., 1., 0.],
      [0., 1., 0., 0., 1.],
      [0., 0., 1., 1., 1.]
    ],
    numpy.double
  ) * (1. + EPSILON)
)
UVL_to_rgb_exp = numpy.max(exp) - 31
UVL_to_rgb = numpy.round(
  numpy.ldexp(UVL_to_rgb, -UVL_to_rgb_exp)
).astype(numpy.int32)

def to_hex(x):
  return '{0:s}0x{1:x}'.format('' if x >= 0 else '-', abs(x))
print(
  '''// generated by ../prepare/uv_to_rgb_gen_c_fixed.py

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
#include "gamma_encode.h"
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

#define EPSILON (1 << 10)

// this is precomputed for the particular primaries in use
int32_t UVL_to_rgb[N_RGB][N_UVL] = {{
  {{{0:s}, {1:s}, {2:s}}},
  {{{3:s}, {4:s}, {5:s}}},
  {{{6:s}, {7:s}, {8:s}}}
}};

// kelv in 16:16 fixed point, results in 2:30 fixed point
void {9:s}(const int32_t *uv, int32_t *rgb) {{
  // validate inputs, allowing a little slack
  assert(uv[UV_u] >= -EPSILON && uv[UV_v] >= -EPSILON && uv[UV_u] + uv[UV_v] < (1 << 30) + EPSILON); 
 
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
  int32_t uv[N_UV] = {{
    (int32_t)ldexpf(atof(argv[1]), 30),
    (int32_t)ldexpf(atof(argv[2]), 30)
  }};

  int32_t rgb[N_RGB];
  {10:s}(uv, rgb);
  printf(
    "uv (%.6f, %.6f) -> RGB (%.6f, %.6f, %.6f)\\n",
    ldexpf(uv[UV_u], -30),
    ldexpf(uv[UV_v], -30),
    ldexpf(rgb[RGB_RED], -30),
    ldexpf(rgb[RGB_GREEN], -30),
    ldexpf(rgb[RGB_BLUE], -30)
  );

  return EXIT_SUCCESS;
}}
#endif'''.format(
    to_hex(UVL_to_rgb[0, 0]),
    to_hex(UVL_to_rgb[0, 1]),
    to_hex(UVL_to_rgb[0, 2]),
    to_hex(UVL_to_rgb[1, 0]),
    to_hex(UVL_to_rgb[1, 1]),
    to_hex(UVL_to_rgb[1, 2]),
    to_hex(UVL_to_rgb[2, 0]),
    to_hex(UVL_to_rgb[2, 1]),
    to_hex(UVL_to_rgb[2, 2]),
    name,
    name
  )
)