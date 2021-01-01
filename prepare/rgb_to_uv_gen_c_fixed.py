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

# put utils into path
# temporary until we have proper Python packaging
import os.path
import sys
dirname = os.path.dirname(__file__)
sys.path.append(os.path.join(dirname, '..'))

import mpmath
import numpy
import utils.yaml_io

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

EPSILON = 1e-8

RGB_RED = 0
RGB_GREEN = 1
RGB_BLUE = 2
N_RGB = 3

UVL_U = 0
UVL_u = 0
UVL_V = 1
UVL_v = 1
UVL_L = 2
N_UVL = 3

mpmath.mp.prec = 106

#numpy.set_printoptions(threshold = numpy.inf)

if len(sys.argv) < 4:
  print(f'usage: {sys.argv[0]:s} model_in.yml gamma_curve device')
  sys.exit(EXIT_FAILURE)
model_in = sys.argv[1]
gamma_curve = sys.argv[2]
device = sys.argv[3]

model = utils.yaml_io._import(utils.yaml_io.read_file(model_in))
primaries_uvL = model['primaries_uvL']

u = primaries_uvL[:, UVL_u]
v = primaries_uvL[:, UVL_v]
L = primaries_uvL[:, UVL_L]
primaries_UVW = numpy.stack([u, v, 1. - u - v], 1) * L[:, numpy.newaxis]

# create a special version in which L = U + V + W
# this makes it easier to convert uv <-> RGB directly
# note: UVL differs from uvL as U, V are scaled by the L
rgb_to_UVL = numpy.array(
  [
    [1., 0., 0.],
    [0., 1., 0.],
    [1., 1., 1.]
  ],
  numpy.double
) @ primaries_UVW.transpose()

# choose precision so that we can store the matrix and also the extreme values
# of the conversion result, which are at all combinations of extreme R, G, B
_, exp = numpy.frexp(
  rgb_to_UVL @ numpy.array(
    [
      [1., 0., 1., 0., 1., 0., 1.],
      [0., 1., 1., 0., 0., 1., 1.],
      [0., 0., 0., 1., 1., 1., 1.]
    ],
    numpy.double
  ) * (1. + EPSILON)
)
rgb_to_UVL_exp = numpy.max(exp) - 31
rgb_to_UVL = numpy.round(
  numpy.ldexp(rgb_to_UVL, -rgb_to_UVL_exp)
).astype(numpy.int32)

print(
  '''// generated by ../prepare/rgb_to_uv_gen_c_fixed.py

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
#include "rgb_to_uv_{0:s}.h"
#include "gamma_decode_{1:s}.h"

#define UV_u 0
#define UV_v 1
#define N_UV 2

#define UVL_u 0
#define UVL_U 0
#define UVL_v 1
#define UVL_V 1
#define UVL_L 2
#define N_UVL 3

#define RGB_RED 0
#define RGB_GREEN 1
#define RGB_BLUE 2
#define N_RGB 3

#define EPSILON (1 << 10)

// this is precomputed for the particular primaries in use
static int32_t rgb_to_UVL[N_UVL][N_RGB] = {{
  {{{2:.8e}f, {3:.8e}f, {4:.8e}f}},
  {{{5:.8e}f, {6:.8e}f, {7:.8e}f}},
  {{{8:.8e}f, {9:.8e}f, {10:.8e}f}}
}};

void rgb_to_uv_{11:s}(const int32_t *rgb, int32_t *uv) {{
  // validate inputs, allowing a little slack
  assert(rgb[RGB_RED] >= -EPSILON && rgb[RGB_RED] < (1 << 30) + EPSILON);
  assert(rgb[RGB_GREEN] >= -EPSILON && rgb[RGB_GREEN] < (1 << 30) + EPSILON);
  assert(rgb[RGB_BLUE] >= -EPSILON && rgb[RGB_BLUE] < (1 << 30) + EPSILON);
  assert((int64_t)rgb[RGB_RED] + rgb[RGB_GREEN] + rgb[RGB_BLUE] >= EPSILON);

  int32_t rgb1[N_RGB];
  for (int i = 0; i < N_RGB; ++i)
    rgb1[i] = gamma_decode_{12:s}(rgb[i]);

  int32_t UVL[N_UVL];
  for (int i = 0; i < N_UVL; ++i) {{
    int64_t v = 1 << 29;
    for (int j = 0; j < N_RGB; ++j)
      v += (int64_t)rgb_to_UVL[i][j] * rgb1[j];
    UVL[i] = (int32_t)(v >> 30);
  }}

  uv[UV_u] = (int32_t)((((int64_t)UVL[UVL_U] << 31) / UVL[UVL_L] + 1) >> 1);
  uv[UV_v] = (int32_t)((((int64_t)UVL[UVL_V] << 31) / UVL[UVL_L] + 1) >> 1);
}}

#ifdef STANDALONE
#include <math.h>
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv) {{
  if (argc < 4) {{
    printf(
      "usage: %s R G B\\n"
        "R = red channel as fraction (0 to 1)\\n"
        "G = green channel as fraction (0 to 1)\\n"
        "B = blue channel as fraction (0 to 1)\\n"
        "R, G and B cannot all be 0\\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }}
  int32_t rgb[N_RGB] = {{
    (int32_t)roundf(ldexpf(atof(argv[1]), 30)),
    (int32_t)roundf(ldexpf(atof(argv[2]), 30)),
    (int32_t)roundf(ldexpf(atof(argv[3]), 30))
  }};

  int32_t uv[N_UV];
  rgb_to_uv_{13:s}(rgb, uv);
  printf(
    "RGB (%.6f, %.6f, %.6f) -> uv (%.6f, %.6f)\\n",
    ldexpf(rgb[RGB_RED], -30),
    ldexpf(rgb[RGB_GREEN], -30),
    ldexpf(rgb[RGB_BLUE], -30),
    ldexpf(uv[UV_u], -30),
    ldexpf(uv[UV_v], -30)
  );

  return EXIT_SUCCESS;
}}
#endif'''.format(
    device,
    gamma_curve,
    rgb_to_UVL[UVL_U, RGB_RED],
    rgb_to_UVL[UVL_U, RGB_GREEN],
    rgb_to_UVL[UVL_U, RGB_BLUE],
    rgb_to_UVL[UVL_V, RGB_RED],
    rgb_to_UVL[UVL_V, RGB_GREEN],
    rgb_to_UVL[UVL_V, RGB_BLUE],
    rgb_to_UVL[UVL_L, RGB_RED],
    rgb_to_UVL[UVL_L, RGB_GREEN],
    rgb_to_UVL[UVL_L, RGB_BLUE],
    device,
    gamma_curve,
    device 
  )
)
