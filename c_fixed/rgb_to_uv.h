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

#ifndef _RGB_TO_UV_H
#define _RGB_TO_UV_H

#include <stdint.h>

#define RGB_TO_UV_N_UVL 3
#define RGB_TO_UV_N_RGB 3

struct rgb_to_uv {
  int32_t (*gamma_decode)(int32_t x);
  int32_t rgb_to_UVL[RGB_TO_UV_N_UVL][RGB_TO_UV_N_RGB];
};

void rgb_to_uv_convert(
  const struct rgb_to_uv *context,
  const int32_t *rgb,
  int32_t *uv
);

#endif
