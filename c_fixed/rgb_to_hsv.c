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
#include <string.h>
#include "rgb_to_hsbk_display_p3.h"
#include "rgb_to_hsbk_rec2020.h"
#include "rgb_to_hsbk_srgb.h"

#define RGB_RED 0
#define RGB_GREEN 1
#define RGB_BLUE 2
#define N_RGB 3

#define HSV_HUE 0
#define HSV_SAT 1
#define HSV_VAL 2
#define N_HSV 3

#define HSBK_HUE 0
#define HSBK_SAT 1
#define HSBK_BR 2
#define HSBK_KELV 3
#define N_HSBK 4

int main(int argc, char **argv) {
  const char *device = "srgb";
  if (argc >= 3 && strcmp(argv[1], "--device") == 0) {
    device = argv[2];
    memmove(argv + 1, argv + 3, (argc - 3) * sizeof(char **));
    argc -= 2;
  }
  if (argc < 3) {
    printf(
      "usage: %s [--device device] image_in image_out [kelv]\n"
        "device in {srgb, display_p3, rec2020}, default srgb\n"
        "image_in = name of PNG file to read\n"
        "image_out = name of PNG file (HSV pixels) to create (will be overwritten)\n"
        "kelv = implicit colour temperature to apply to HSV pixels (default 6504K)\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }
  const char *image_in = argv[1];
  const char *image_out = argv[2];
  int32_t kelv =
    argc >= 4 ? (int32_t)roundf(ldexpf(atof(argv[3]), 16)) : (int32_t)0;

  FILE *fp = fopen(image_in, "r");
  if (fp == NULL) {
    perror(image_in);
    exit(EXIT_FAILURE);
  }

  const struct rgb_to_hsbk *rgb_to_hsbk;
  if (strcmp(device, "srgb") == 0)
    rgb_to_hsbk = &rgb_to_hsbk_srgb;
  else if (strcmp(device, "display_p3") == 0)
    rgb_to_hsbk = &rgb_to_hsbk_display_p3;
  else if (strcmp(device, "rec2020") == 0)
    rgb_to_hsbk = &rgb_to_hsbk_rec2020;
  else
    abort();

  png_structp png_ptr = png_create_read_struct(
    PNG_LIBPNG_VER_STRING,
    NULL,
    NULL,
    NULL
  );
  if (png_ptr == NULL) {
    perror("png_create_read_struct()");
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

  png_read_info(png_ptr, info_ptr);

  if (png_get_bit_depth(png_ptr, info_ptr) != 8) {
    fprintf(stderr, "require 8 bit image\n");
    exit(EXIT_FAILURE);
  }
  if (png_get_channels(png_ptr, info_ptr) != 3) {
    fprintf(stderr, "require 3 channel image\n");
    exit(EXIT_FAILURE);
  }
  int size_x = png_get_image_width(png_ptr, info_ptr);
  int size_y = png_get_image_height(png_ptr, info_ptr);

  png_byte *pixels = malloc(size_y * size_x * N_RGB * sizeof(png_byte));
  if (pixels == NULL) {
    perror("malloc()");
    exit(EXIT_FAILURE);
  }

  png_byte **rows = malloc(size_y * sizeof(png_byte *));
  if (rows == NULL) {
    perror("malloc()");
    exit(EXIT_FAILURE);
  }
  for (int i = 0; i < size_y; ++i)
    rows[i] = pixels + i * size_x * N_RGB;

  png_read_image(png_ptr, rows);

  int32_t *image = malloc(size_y * size_x * N_RGB * sizeof(int32_t));
  if (image == NULL) {
    perror("malloc()");
    exit(EXIT_FAILURE);
  }
  for (int i = 0; i < size_y; ++i)
    for (int j = 0; j < size_x; ++j)
      for (int k = 0; k < N_RGB; ++k)
        image[(i * size_x + j) * N_RGB + k] = (uint32_t)(
          (
            (
              (int64_t)pixels[(i * size_x + j) * N_RGB + k] << 31
            ) / 255 + 1
          ) >> 1
        );
  png_read_end(png_ptr, NULL);
  fclose(fp);

  for (int i = 0; i < size_y; ++i) {
    //printf("%d / %d\n", i, size_y);
    for (int j = 0; j < size_x; ++j) {
      int32_t hsbk[N_HSBK];
      rgb_to_hsbk_convert(
        rgb_to_hsbk,
        image + (i * size_x + j) * N_RGB,
        kelv,
        hsbk
      );
      memcpy(
        image + (i * size_x + j) * N_RGB,
        hsbk,
        N_HSV * sizeof(int32_t)
      );
    }
  }

  fp = fopen(image_out, "wb");
  if (fp == NULL) {
    perror(image_out);
    exit(EXIT_FAILURE);
  }

  png_ptr = png_create_write_struct(
    PNG_LIBPNG_VER_STRING,
    NULL,
    NULL,
    NULL
  );
  if (png_ptr == NULL) {
    perror("png_create_write_struct()");
    exit(EXIT_FAILURE);
  }

  info_ptr = png_create_info_struct(png_ptr);
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
    size_x,
    size_y,
    8,
    PNG_COLOR_TYPE_RGB,
    PNG_INTERLACE_NONE,
    PNG_COMPRESSION_TYPE_BASE,
    PNG_FILTER_TYPE_BASE
  );

  png_write_info(png_ptr, info_ptr);

  for (int i = 0; i < size_y; ++i)
    for (int j = 0; j < size_x; ++j) {
      pixels[(i * size_x + j) * N_HSV + HSV_HUE] = (png_byte)(
        (image[(i * size_x + j) * N_HSV + HSV_HUE] + (1 << 23)) >> 24
      );
      pixels[(i * size_x + j) * N_HSV + HSV_SAT] = (png_byte)(
        (image[(i * size_x + j) * N_HSV + HSV_SAT] * 255LL + (1 << 29)) >> 30
      );
      pixels[(i * size_x + j) * N_HSV + HSV_VAL] = (png_byte)(
        (image[(i * size_x + j) * N_HSV + HSV_VAL] * 255LL + (1 << 29)) >> 30
      );
    }
  free(image);

  png_write_image(png_ptr, rows);

  free(pixels);
  free(rows);

  png_write_end(png_ptr, NULL);
  fclose(fp);

  return EXIT_SUCCESS;
}
