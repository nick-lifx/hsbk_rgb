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
//#include <stdio.h>
#include "kelv_to_uv_deriv.h"
#include "uv_to_kelv.h"

#define UV_u 0
#define UV_v 1
#define N_UV 2

#define XY_x 0
#define XY_y 1
#define N_XY 2

#define EPSILON 1e-6f

// kelv_uv and/or duv can be NULL
float uv_to_kelv(const float *uv, float *kelv_uv, float *duv) {
  // validate inputs, allowing a little slack
  assert(uv[UV_u] >= -EPSILON && uv[UV_v] >= -EPSILON && uv[UV_u] + uv[UV_v] < 1.f + EPSILON); 

  // convert to xy for McCamy's approximation
  // see https://en.wikipedia.org/wiki/CIE_1960_color_space#Relation_to_CIE_XYZ
  float denom = uv[UV_u] * 2.f - uv[UV_v] * 8.f + 4.f;
  float xy[N_XY] = {uv[UV_u] * 3.f / denom, uv[UV_v] * 2.f / denom};
  //printf("xy %f %f\n", xy[XY_x], xy[XY_y]);
  assert(xy[XY_y] >= .1858f + EPSILON);

  // make initial estimate by McCamy's approximation
  // see https://en.wikipedia.org/wiki/Color_temperature#Approximation
  // does not work well below 1500K, but the loop below can recover OK
  float n = (xy[XY_x] - .3320f) / (xy[XY_y] - .1858f);
  float x = -449.f;
  x = x * n + 3525.f;
  x = x * n - 6823.3f;
  x = x * n + 5520.33f;
  //printf("x %f\n", x);

  // refine initial estimate with Newton's method
  float y_deriv[N_UV], y[N_UV], y_to_uv[N_UV];
  for (int i = 0; ; ++i) {
    if (x < 1000.f)
      x = 1000.f;
    else if (x > 15000.f)
      x = 15000.f;
    kelv_to_uv_deriv(x, y_deriv, y);
    y_to_uv[UV_u] = uv[UV_u] - y[UV_u];
    y_to_uv[UV_v] = uv[UV_v] - y[UV_v];
    //printf(
    //  "i %d x %f y %f %f y_deriv %f %f y_to_uv %f %f\n",
    //  i,
    //  x,
    //  y[UV_u],
    //  y[UV_v],
    //  y_deriv[UV_u],
    //  y_deriv[UV_v],
    //  y_to_uv[UV_u],
    //  y_to_uv[UV_v]
    //);
    if (i >= 5)
      break;
    x += (
      y_deriv[UV_u] * y_to_uv[UV_u] + y_deriv[UV_v] * y_to_uv[UV_v]
    ) / (
      y_deriv[UV_u] * y_deriv[UV_u] + y_deriv[UV_v] * y_deriv[UV_v]
    );
  }

  if (kelv_uv) {
    kelv_uv[UV_u] = y[UV_u];
    kelv_uv[UV_v] = y[UV_v];
  }
  if (duv) {
    float y_normal[N_UV] = {-y_deriv[UV_v], y_deriv[UV_u]};
    denom = sqrtf(
      y_normal[UV_u] * y_normal[UV_u] + y_normal[UV_v] * y_normal[UV_v]
    );
    y_normal[UV_u] /= denom;
    y_normal[UV_v] /= denom;
    *duv = y_to_uv[UV_u] * y_normal[UV_u] + y_to_uv[UV_v] * y_normal[UV_v];
  } 
  return x;
}

#ifdef STANDALONE
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv) {
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

  float duv;
  float kelv = uv_to_kelv(uv, NULL, &duv);
  printf(
    "uv (%.6f, %.6f) -> kelv %.3f duv %.6f\n",
    uv[UV_u],
    uv[UV_v],
    kelv,
    duv
  );

  return EXIT_SUCCESS;
}
#endif
