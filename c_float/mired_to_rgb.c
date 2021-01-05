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
#include "mired_to_rgb.h"

#define RGB_RED 0
#define RGB_GREEN 1
#define RGB_BLUE 2
#define N_RGB 3

#define MIRED_MIN (1e6f / 15000.f)
#define MIRED_MAX (1e6f / 1000.f)

#define EPSILON 1e-6

void mired_to_rgb_convert(
  const struct mired_to_rgb *context,
  float mired,
  float *rgb
) {
  // validate inputs, allowing a little slack
  assert(mired >= MIRED_MIN * (1.f - EPSILON) && mired < MIRED_MAX * (1.f + EPSILON));

  // calculate red channel
  float r;
  if (mired < context->b_red) {
    // below assumes ORDER_RED_AB == 4
    r = context->p_red_ab[3];
    r = r * mired + context->p_red_ab[2];
    r = r * mired + context->p_red_ab[1];
    r = r * mired + context->p_red_ab[0];
  }
  else
    r = 1.f;
  rgb[RGB_RED] = r;

  // calculate green channel
  float g;
  if (mired < context->b_green) {
    // below assumes ORDER_GREEN_AB == 4
    g = context->p_green_ab[3];
    g = g * mired + context->p_green_ab[2];
    g = g * mired + context->p_green_ab[1];
    g = g * mired + context->p_green_ab[0];
  }
  else {
    // below assumes ORDER_GREEN_BD == 6
    g = context->p_green_bd[5];
    g = g * mired + context->p_green_bd[4];
    g = g * mired + context->p_green_bd[3];
    g = g * mired + context->p_green_bd[2];
    g = g * mired + context->p_green_bd[1];
    g = g * mired + context->p_green_bd[0];
  }
  rgb[RGB_GREEN] = g;

  // calculate blue channel
  float b;
  if (mired < context->b_blue)
    b = 1.f;
  else if (mired < context->c_blue) {
    // below assumes ORDER_BLUE_BC == 8
    b = context->p_blue_bc[7];
    b = b * mired + context->p_blue_bc[6];
    b = b * mired + context->p_blue_bc[5];
    b = b * mired + context->p_blue_bc[4];
    b = b * mired + context->p_blue_bc[3];
    b = b * mired + context->p_blue_bc[2];
    b = b * mired + context->p_blue_bc[1];
    b = b * mired + context->p_blue_bc[0];
  }
  else
    b = 0.f;
  rgb[RGB_BLUE] = b;
}

#ifdef STANDALONE
#include <stdlib.h>
#include <stdio.h>

void mired_to_rgb_standalone(
  const struct mired_to_rgb *context,
  int argc,
  char **argv
) {
  if (argc < 2) {
    printf(
      "usage: %s mired\n"
        "mired = colour temperature in micro reciprocal degrees Kelvin\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }
  float mired = atof(argv[1]);

  float rgb[N_RGB];
  mired_to_rgb_convert(context, mired, rgb);
  printf(
    "mired %.3f -> RGB (%.6f, %.6f, %.6f)\n",
    mired,
    rgb[RGB_RED],
    rgb[RGB_GREEN],
    rgb[RGB_BLUE]
  );
}
#endif
