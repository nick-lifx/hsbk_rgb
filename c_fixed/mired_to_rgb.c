// generated by ../prepare/mired_to_rgb_gen_c_fixed.py

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

#define EPSILON (1 << 6)

void mired_to_rgb(int32_t mired, int32_t *rgb) {
  // validate inputs, allowing a little slack
  assert(mired >= 0x42aaab - EPSILON && mired < 0x3e80000 + EPSILON);

  // calculate red channel
  int32_t r;
  if (mired < 0x99038b) {
    r = 0x87f70;
    r = (int32_t)(((int64_t)r * mired + 0x49e2362d0d8aLL) >> 23);
    r = (int32_t)(((int64_t)r * mired + 0x5474dc72f140LL) >> 25);
    r = (int32_t)(((int64_t)r * mired + 0x4a8cb6fcdd01LL) >> 17);
  }
  else {
    r = 0x40000000;
  }
  rgb[RGB_RED] = r;

  // calculate green channel
  int32_t g;
  if (mired < 0x996334) {
    g = -0xde1d3;
    g = (int32_t)(((int64_t)g * mired + 0x5e56890a0439LL) >> 24);
    g = (int32_t)(((int64_t)g * mired + 0x465d2cb3a376LL) >> 25);
    g = (int32_t)(((int64_t)g * mired + 0x587d7d9bad57LL) >> 17);
  }
  else {
    g = -0x68654;
    g = (int32_t)(((int64_t)g * mired + 0x4215a9271dabLL) >> 26);
    g = (int32_t)(((int64_t)g * mired - 0x45df4c95bf4aLL) >> 25);
    g = (int32_t)(((int64_t)g * mired + 0x5607d859f21eLL) >> 25);
    g = (int32_t)(((int64_t)g * mired - 0x5cd42666d46dLL) >> 25);
    g = (int32_t)(((int64_t)g * mired + 0x5438fa17c054LL) >> 16);
  }
  rgb[RGB_GREEN] = g;

  // calculate blue channel
  int32_t b;
  if (mired < 0x98c246) {
    b = 0x40000000;
  }
  else if (mired < 0x20df5c4) {
    b = -0xe5182;
    b = (int32_t)(((int64_t)b * mired + 0x614cbd531dadLL) >> 25);
    b = (int32_t)(((int64_t)b * mired - 0x7c0a9b061670LL) >> 25);
    b = (int32_t)(((int64_t)b * mired + 0x42289b9610ffLL) >> 21);
    b = (int32_t)(((int64_t)b * mired - 0x49a60a958692LL) >> 26);
    b = (int32_t)(((int64_t)b * mired - 0x40fc86456de5LL) >> 21);
    b = (int32_t)(((int64_t)b * mired + 0x514d7f78c2a8LL) >> 26);
    b = (int32_t)(((int64_t)b * mired + 0x572f506ce8caLL) >> 16);
  }
  else {
    b = 0x0;
  }
  rgb[RGB_BLUE] = b;
}

#ifdef STANDALONE
#include <math.h>
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv) {
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
  mired_to_rgb(mired, rgb);
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
