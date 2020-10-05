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

#include <errno.h>
#include <math.h>
#include <png.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include "hsbk_to_rgb.h"

#define RGB_RED 0
#define RGB_GREEN 1
#define RGB_BLUE 2
#define N_RGB 3

#define HSBK_HUE 0
#define HSBK_SAT 1
#define HSBK_BR 2
#define HSBK_KELV 3
#define N_HSBK 4

#define EPSILON 1e-6f

int main(int argc, char **argv) {
  if (argc < 4) {
    printf(
      "usage: %s sat br image_out\n"
        "sat = saturation as fraction (0 to 1)\n"
        "br = brightness as fraction (0 to 1)\n"
        "image_out = name of PNG file to create (will be overwritten)\n"
        "creates 361 x 376 x 3 image with 0..360 degrees by 1, 1500..9000 Kelvin by 20\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }
  float sat = atof(argv[1]);
  float br = atof(argv[2]);
  char *image_out = argv[3];

  float image[376][361][N_RGB];
  for (int i = 0; i < 376; ++i) {
    //printf("%d / 376\n", i);
    float kelv = 1500.f + 20.f * i;
    for (int j = 0; j < 361; ++j) {
      float hue = 1.f * j;
      float hsbk[N_HSBK] = {hue, sat, br, kelv};
      hsbk_to_rgb(hsbk, image[i][j]);
    }
  }

  FILE *fp = fopen(image_out, "wb");
  if (fp == NULL) {
    perror(image_out);
    exit(EXIT_FAILURE);
  }

  png_structp png_ptr = png_create_write_struct(
    PNG_LIBPNG_VER_STRING,
    NULL,
    NULL,
    NULL
  );
  if (png_ptr == NULL) {
    perror("png_create_write_struct()");
    exit(EXIT_FAILURE);
  }

  png_infop info_ptr = png_create_info_struct(png_ptr);
  if (info_ptr == NULL) {
    perror("png_create_info_struct()");
    exit(EXIT_FAILURE);
  }

  if (setjmp(png_jmpbuf(png_ptr))) {
    perror("setjmp()");
    exit(EXIT_FAILURE);
  }
  png_init_io(png_ptr, fp);

  png_set_IHDR(
    png_ptr,
    info_ptr,
    361,
    376,
    8,
    PNG_COLOR_TYPE_RGB,
    PNG_INTERLACE_NONE,
    PNG_COMPRESSION_TYPE_BASE,
    PNG_FILTER_TYPE_BASE
  );

  png_write_info(png_ptr, info_ptr);

  png_byte pixels[376][361][N_RGB];
  for (int i = 0; i < 376; ++i)
    for (int j = 0; j < 361; ++j)
      for (int k = 0; k < N_RGB; ++k)
        pixels[i][j][k] = (png_byte)roundf(image[i][j][k] * 255.f);

  png_byte *rows[376];
  for (int i = 0; i < 376; ++i)
    rows[i] = pixels[i][0];

  png_write_image(png_ptr, rows);

  png_write_end(png_ptr, NULL);
  fclose(fp);

  return EXIT_SUCCESS;
}
