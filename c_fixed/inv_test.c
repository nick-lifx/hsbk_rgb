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
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "hsbk_to_rgb_display_p3.h"
#include "hsbk_to_rgb_rec2020.h"
#include "hsbk_to_rgb_srgb.h"
#include "rgb_to_hsbk_display_p3.h"
#include "rgb_to_hsbk_rec2020.h"
#include "rgb_to_hsbk_srgb.h"

#define RGB_RED 0
#define RGB_GREEN 1
#define RGB_BLUE 2
#define N_RGB 3

#define HSBK_HUE 0
#define HSBK_SAT 1
#define HSBK_BR 2
#define HSBK_KELV 3
#define N_HSBK 4

#define EPSILON (1 << 10)

int main(int argc, char **argv) {
  const char *device = "srgb";
  if (argc >= 3 && strcmp(argv[1], "--device") == 0) {
    device = argv[2];
    memmove(argv + 1, argv + 3, (argc - 3) * sizeof(char **));
    argc -= 2;
  }
  if (argc < 3) {
    printf(
      "usage: %s [--device device] seed count [kelv]\n"
        "device in {srgb, display_p3, rec2020}, default srgb\n"
        "checks invertibility of the RGB -> HSBK -> RGB pipeline\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }
  int seed = atoi(argv[1]);
  int count = atoi(argv[2]);
  int32_t kelv =
    argc >= 4 ? (int32_t)roundf(ldexpf(atof(argv[3]), 16)) : (int32_t)0;

  const struct hsbk_to_rgb *hsbk_to_rgb;
  void (*rgb_to_hsbk)(const int32_t *rgb, int32_t kelv, int32_t *hsbk);
  if (strcmp(device, "srgb") == 0) {
    hsbk_to_rgb = &hsbk_to_rgb_srgb;
    rgb_to_hsbk = rgb_to_hsbk_srgb;
  }
  else if (strcmp(device, "display_p3") == 0) {
    hsbk_to_rgb = &hsbk_to_rgb_display_p3;
    rgb_to_hsbk = rgb_to_hsbk_display_p3;
  }
  else if (strcmp(device, "rec2020") == 0) {
    hsbk_to_rgb = &hsbk_to_rgb_rec2020;
    rgb_to_hsbk = rgb_to_hsbk_rec2020;
  }
  else
    abort();

  srand(seed);
  for (int i = 0; i < count; ++i) {
    int32_t rgb[N_RGB];
    for (int j = 0; j < N_RGB; ++j)
      rgb[j] = ((int64_t)rand() << 30) / RAND_MAX;
 printf("%f %f %f\n", ldexpf(rgb[0], -30), ldexpf(rgb[1], -30), ldexpf(rgb[2], -30));
    int32_t hsbk[N_HSBK];
    rgb_to_hsbk(rgb, kelv, hsbk);
    int32_t rgb1[N_RGB];
    hsbk_to_rgb_convert(hsbk_to_rgb, hsbk, rgb1);
    for (int j = 0; j < N_RGB; ++j) {
      printf("%x %x %x -> %x %x %x\n", rgb1[0], rgb1[1], rgb1[2], rgb[0], rgb[1], rgb[2]);
      assert(abs(rgb1[j] - rgb[j]) < EPSILON);
    }
  }

  return EXIT_SUCCESS;
}
