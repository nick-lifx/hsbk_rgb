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

#include <stdio.h>
#include "hsbk_to_rgb.h"

#define EXIT_SUCCESS 0
#define EXIT_FAILURE 1

#define HSBK_HUE 0
#define HSBK_SAT 1
#define HSBK_BR 2
#define HSBK_KELV 3
#define N_HSBK 4

#define RGB_RED 0
#define RGB_GREEN 1
#define RGB_BLUE 2
#define N_RGB 3

// precompute RGB for 6504K, used for rgb_to_hsbk with kelv == 0

int main(void) {
  int32_t hsbk[N_HSBK] = {0, 0, 1 << 30, 6504 << 16};
  int32_t rgb[N_RGB];
  hsbk_to_rgb(hsbk, rgb);
  printf(
    "static int32_t kelv_rgb_6504K[N_RGB] = {\n"
      "  0x%x,\n"
      "  0x%x,\n"
      "  0x%x\n"
      "};\n",
      rgb[RGB_RED],
      rgb[RGB_GREEN],
      rgb[RGB_BLUE]
  );
  return EXIT_SUCCESS;
}