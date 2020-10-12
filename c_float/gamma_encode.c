// generated by ../prepare/gamma_encode_gen_c_float.py

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
#include "gamma_encode.h"

static float post_factor[] = {
  9.92125657e-02f,
  1.32432887e-01f,
  1.76776695e-01f,
  2.35968578e-01f,
  3.14980262e-01f,
  4.20448208e-01f,
  5.61231024e-01f,
  7.49153538e-01f,
  1.00000000e+00f,
  1.33483985e+00f
};

// returns approximation to:
//   x < .0031308f ? x * 12.92f : powf(x, 1.f / 2.4f) * 1.055f - .055f
// allowed domain (-inf, 2), recommended domain [-epsilon, 1 + epsilon)
// minimax error is up to 3.018057e-08 relative
float gamma_encode(float x) {
  if (x < .0031308f)
    return x * 12.92f;
  int exp;
  x = frexpf(x, &exp);
  assert(exp < 2);
  float y = 1.62916011e-01f;
  y = y * x - 9.93910045e-01f;
  y = y * x + 2.66279255e+00f;
  y = y * x - 4.12665575e+00f;
  y = y * x + 4.12604477e+00f;
  y = y * x - 2.88667285e+00f;
  y = y * x + 1.85050989e+00f;
  y = y * x + 2.59975447e-01f;
  return y * post_factor[exp + 8] - .055f;
}

#ifdef STANDALONE
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv) {
  if (argc < 2) {
    printf(
      "usage: %s x\n"
        "x = linear intensity, calculates gamma encoded intensity\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }
  float x = atof(argv[1]);

  float y = gamma_encode(x);
  printf("linear %.6f -> gamma encoded %.6f\n", x, y);

  return EXIT_SUCCESS;
}
#endif
