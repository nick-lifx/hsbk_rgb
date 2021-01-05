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

// below are 1e6 / 15000 and 1e6 / 1000 in 16:16 fixed point
#define MIRED_MIN 0x42aaab
#define MIRED_MAX 0x3e80000

#define EPSILON (1 << 6)

void mired_to_rgb_convert(
  const struct mired_to_rgb *context,
  int32_t mired,
  int32_t *rgb
) {
  // validate inputs, allowing a little slack
  assert(mired >= MIRED_MIN - EPSILON && mired < MIRED_MAX + EPSILON);

  // calculate red channel
  int32_t r;
  if (mired < context->b_red) {
    // below assumes ORDER_RED_AB == 4
    r = (int32_t)context->p_red_ab[3];
    r = (int32_t)(
      ((int64_t)r * mired + context->p_red_ab[2]) >>
        context->p_red_ab_shr[2]
    );
    r = (int32_t)(
      ((int64_t)r * mired + context->p_red_ab[1]) >>
        context->p_red_ab_shr[1]
    );
    r = (int32_t)(
      ((int64_t)r * mired + context->p_red_ab[0]) >>
        context->p_red_ab_shr[0]
    );
  }
  else
    r = 1 << 30;
  rgb[RGB_RED] = r;

  // calculate green channel
  int32_t g;
  if (mired < context->b_green) {
    // below assumes ORDER_GREEN_AB == 4
    g = (int32_t)context->p_green_ab[3];
    g = (int32_t)(
      ((int64_t)g * mired + context->p_green_ab[2]) >>
        context->p_green_ab_shr[2]
    );
    g = (int32_t)(
      ((int64_t)g * mired + context->p_green_ab[1]) >>
        context->p_green_ab_shr[1]
    );
    g = (int32_t)(
      ((int64_t)g * mired + context->p_green_ab[0]) >>
        context->p_green_ab_shr[0]
    );
  }
  else {
    // below assumes ORDER_GREEN_BD == 6
    g = (int32_t)context->p_green_bd[5];
    g = (int32_t)(
      ((int64_t)g * mired + context->p_green_bd[4]) >>
        context->p_green_bd_shr[4]
    );
    g = (int32_t)(
      ((int64_t)g * mired + context->p_green_bd[3]) >>
        context->p_green_bd_shr[3]
    );
    g = (int32_t)(
      ((int64_t)g * mired + context->p_green_bd[2]) >>
        context->p_green_bd_shr[2]
    );
    g = (int32_t)(
      ((int64_t)g * mired + context->p_green_bd[1]) >>
        context->p_green_bd_shr[1]
    );
    g = (int32_t)(
      ((int64_t)g * mired + context->p_green_bd[0]) >>
        context->p_green_bd_shr[0]
    );
  }
  rgb[RGB_GREEN] = g;

  // calculate blue channel
  int32_t b;
  if (mired < context->b_blue)
    b = 1 << 30;
  else if (mired < context->c_blue) {
    // below assumes ORDER_BLUE_BC == 8
    b = (int32_t)context->p_blue_bc[7];
    b = (int32_t)(
      ((int64_t)b * mired + context->p_blue_bc[6]) >>
        context->p_blue_bc_shr[6]
    );
    b = (int32_t)(
      ((int64_t)b * mired + context->p_blue_bc[5]) >>
        context->p_blue_bc_shr[5]
    );
    b = (int32_t)(
      ((int64_t)b * mired + context->p_blue_bc[4]) >>
        context->p_blue_bc_shr[4]
    );
    b = (int32_t)(
      ((int64_t)b * mired + context->p_blue_bc[3]) >>
        context->p_blue_bc_shr[3]
    );
    b = (int32_t)(
      ((int64_t)b * mired + context->p_blue_bc[2]) >>
        context->p_blue_bc_shr[2]
    );
    b = (int32_t)(
      ((int64_t)b * mired + context->p_blue_bc[1]) >>
        context->p_blue_bc_shr[1]
    );
    b = (int32_t)(
      ((int64_t)b * mired + context->p_blue_bc[0]) >>
        context->p_blue_bc_shr[0]
    );
  }
  else
    b = 0;
  rgb[RGB_BLUE] = b;
}

#ifdef STANDALONE
#include <math.h>
#include <stdlib.h>
#include <stdio.h>

int mired_to_rgb_standalone(
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
  int32_t mired = (int32_t)roundf(ldexpf(atof(argv[1]), 16));

  int32_t rgb[N_RGB];
  mired_to_rgb_convert(context, mired, rgb);
  printf(
    "mired %.3f -> RGB (%.6f, %.6f, %.6f)\n",
    ldexpf(mired, -16),
    ldexpf(rgb[RGB_RED], -30),
    ldexpf(rgb[RGB_GREEN], -30),
    ldexpf(rgb[RGB_BLUE], -30)
  );

  return EXIT_SUCCESS;
}
#endif
