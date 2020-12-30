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

import numpy
import utils.yaml_io

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

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

print(
  '''// generated by ../prepare/rgb_to_uv_gen_c_float.py

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

#define UVL_U 0
#define UVL_V 1
#define UVL_L 2
#define N_UVL 3

#define RGB_RED 0
#define RGB_GREEN 1
#define RGB_BLUE 2
#define N_RGB 3

#define EPSILON 1e-6f

// this is precomputed for the particular primaries in use
static float rgb_to_UVL[N_UVL][N_RGB] = {{
  {{{2:.8e}f, {3:.8e}f, {4:.8e}f}},
  {{{5:.8e}f, {6:.8e}f, {7:.8e}f}},
  {{{8:.8e}f, {9:.8e}f, {10:.8e}f}}
}};

void rgb_to_uv_{11:s}(const float *rgb, float *uv) {{
  // validate inputs, allowing a little slack
  assert(rgb[RGB_RED] >= -EPSILON && rgb[RGB_RED] < 1.f + EPSILON);
  assert(rgb[RGB_GREEN] >= -EPSILON && rgb[RGB_GREEN] < 1.f + EPSILON);
  assert(rgb[RGB_BLUE] >= -EPSILON && rgb[RGB_BLUE] < 1.f + EPSILON);
  assert(rgb[RGB_RED] + rgb[RGB_GREEN] + rgb[RGB_BLUE] >= EPSILON);

  float rgb1[N_RGB];
  for (int i = 0; i < N_RGB; ++i)
    rgb1[i] = gamma_decode_{12:s}(rgb[i]);

  float UVL[N_UVL];
  for (int i = 0; i < N_UVL; ++i) {{
    float v = 0.f;
    for (int j = 0; j < N_RGB; ++j)
      v += rgb_to_UVL[i][j] * rgb1[j];
    UVL[i] = v;
  }}

  uv[UV_u] = UVL[UVL_U] / UVL[UVL_L];
  uv[UV_v] = UVL[UVL_V] / UVL[UVL_L];
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
  float rgb[N_RGB] = {{atof(argv[1]), atof(argv[2]), atof(argv[3])}};

  float uv[N_UV];
  rgb_to_uv_{13:s}(rgb, uv);
  printf(
    "RGB (%.6f, %.6f, %.6f) -> uv (%.6f, %.6f)\\n",
    rgb[RGB_RED],
    rgb[RGB_GREEN],
    rgb[RGB_BLUE],
    uv[UV_u],
    uv[UV_v]
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
