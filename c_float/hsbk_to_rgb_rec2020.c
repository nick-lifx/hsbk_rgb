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

#include "hsbk_to_rgb.h"
#include "mired_to_rgb_rec2020.h"

void hsbk_to_rgb_rec2020(const float *hsbk, float *rgb) {
  hsbk_to_rgb(&mired_to_rgb_rec2020, hsbk, rgb);
}

#ifdef STANDALONE
int hsbk_to_rgb_standalone(
  void (*_hsbk_to_rgb)(const float *hsbk, float *rgb),
  int argc,
  char **argv
);

int main(int argc, char **argv) {
  return hsbk_to_rgb_standalone(hsbk_to_rgb_rec2020, argc, argv);
}
#endif
