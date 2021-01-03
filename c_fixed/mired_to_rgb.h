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

#ifndef _MIRED_TO_RGB_H
#define _MIRED_TO_RGB_H

#include <stdint.h>

#define MIRED_TO_RGB_ORDER_RED_AB 4
#define MIRED_TO_RGB_ORDER_GREEN_AB 4
#define MIRED_TO_RGB_ORDER_GREEN_BD 6
#define MIRED_TO_RGB_ORDER_BLUE_BC 8

struct mired_to_rgb {
  int32_t b_red;
  int32_t b_green;
  int32_t b_blue;
  int32_t c_blue;
  int64_t p_red_ab[MIRED_TO_RGB_ORDER_RED_AB];
  int64_t p_green_ab[MIRED_TO_RGB_ORDER_GREEN_AB];
  int64_t p_green_bd[MIRED_TO_RGB_ORDER_GREEN_BD];
  int64_t p_blue_bc[MIRED_TO_RGB_ORDER_BLUE_BC];
  uint8_t p_red_ab_shr[MIRED_TO_RGB_ORDER_RED_AB - 1];
  uint8_t p_green_ab_shr[MIRED_TO_RGB_ORDER_GREEN_AB - 1];
  uint8_t p_green_bd_shr[MIRED_TO_RGB_ORDER_GREEN_BD - 1];
  uint8_t p_blue_bc_shr[MIRED_TO_RGB_ORDER_BLUE_BC - 1];
};

void mired_to_rgb_convert(
  const struct mired_to_rgb *context,
  int32_t mired,
  int32_t *rgb
);

#endif
