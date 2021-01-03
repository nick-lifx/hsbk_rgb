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
#include "hsbk_to_rgb_rec2020.h"
#include "hsbk_to_rgb_display_p3.h"
#include "hsbk_to_rgb_srgb.h"
#include "rgb_to_uv_rec2020.h"
#include "rgb_to_uv_display_p3.h"
#include "rgb_to_uv_srgb.h"

#define RGB_RED 0
#define RGB_GREEN 1
#define RGB_BLUE 2
#define N_RGB 3

#define HSBK_HUE 0
#define HSBK_SAT 1
#define HSBK_BR 2
#define HSBK_KELV 3
#define N_HSBK 4

#define UV_u 0
#define UV_v 1
#define N_UV 2

int main(int argc, char **argv) {
  const char *device = "srgb";
  if (argc >= 3 && strcmp(argv[1], "--device") == 0) {
    device = argv[2];
    memmove(argv + 1, argv + 3, (argc - 3) * sizeof(char **));
    argc -= 2;
  }
  if (argc < 2) {
    printf(
      "usage: %s [--device device] image_out\n"
        "device in {srgb, display_p3, rec2020}, default srgb\n"
        "image_out = name of PNG file to create (will be overwritten)\n"
        "creates 361 x 376 image with 0..360 degrees by 1, 1500..9000 Kelvin by 20\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }
  const char *image_out = argv[1];

  const struct hsbk_to_rgb *hsbk_to_rgb;
  const struct rgb_to_uv *rgb_to_uv;
  if (strcmp(device, "srgb") == 0) {
    hsbk_to_rgb = &hsbk_to_rgb_srgb;
    rgb_to_uv = &rgb_to_uv_srgb;
  }
  else if (strcmp(device, "display_p3") == 0) {
    hsbk_to_rgb = &hsbk_to_rgb_display_p3;
    rgb_to_uv = &rgb_to_uv_display_p3;
  }
  else if (strcmp(device, "rec2020") == 0) {
    hsbk_to_rgb = &hsbk_to_rgb_rec2020;
    rgb_to_uv = &rgb_to_uv_rec2020;
  }
  else
    abort();

  // find chromaticities of the hue space by 1 degree increments
  int32_t hue_uv[361][N_UV];
  for (int i = 0; i < 361; ++i) {
    int32_t hsbk[N_HSBK] = {
      (int32_t)((((int64_t)i << 33) / 360 + 1) >> 1),
      1 << 30,
      1 << 30,
      6504 << 16
    };
    int32_t rgb[N_RGB];
    hsbk_to_rgb_convert(hsbk_to_rgb, hsbk, rgb);
    rgb_to_uv_convert(rgb_to_uv, rgb, hue_uv[i]);
  }

  // find chromaticities of the Kelvin space by 20 degree increments
  int32_t kelv_uv[376][N_UV];
  for (int i = 0; i < 376; ++i) {
    int32_t hsbk[N_HSBK] = {
      0,
      0,
      1 << 30,
      (1500 << 16) + (20 << 16) * i
    };
    int32_t rgb[N_RGB];
    hsbk_to_rgb_convert(hsbk_to_rgb, hsbk, rgb);
    rgb_to_uv_convert(rgb_to_uv, rgb, kelv_uv[i]);
  }

  // find chromaticities of the hue x Kelvin space @ saturation .5, then
  // convert each chromaticity to a weighting between hue_uv and kelv_uv
  int32_t image[376][361];
  for (int i = 0; i < 376; ++i) {
    //printf("%d / 376\n", i);
    int32_t kelv = (1500 << 16) + (20 << 16) * i;
    int32_t v0[N_UV] = {
      kelv_uv[i][UV_u],
      kelv_uv[i][UV_v]
    };
    for (int j = 0; j < 361; ++j) {
      int32_t hue = (int32_t)((((int64_t)j << 33) / 360 + 1) >> 1);
      int32_t v1[N_UV] = {
        hue_uv[j][UV_u] - v0[UV_u],
        hue_uv[j][UV_v] - v0[UV_v]
      };
      int32_t hsbk[N_HSBK] = {hue, 1 << 29, 1 << 30, kelv};
      int32_t rgb[N_RGB];
      hsbk_to_rgb_convert(hsbk_to_rgb, hsbk, rgb);
      int32_t uv[N_UV];
      rgb_to_uv_convert(rgb_to_uv, rgb, uv);
      int32_t w_num = (int32_t)(
        (
          (int64_t)(uv[UV_u] - v0[UV_u]) * v1[UV_u] +
            (int64_t)(uv[UV_v] - v0[UV_v]) * v1[UV_v] +
            (1 << 29)
        ) >> 30
      );
      int32_t w_denom = (int32_t)(
        (
          (int64_t)v1[UV_u] * v1[UV_u] +
            (int64_t)v1[UV_v] * v1[UV_v] +
            (1 << 29)
        ) >> 30
      );
      if (w_denom == 0)
        w_denom = 1; // there seems to be a loss of precision (revisit later)
      int32_t w = (int32_t)((((int64_t)w_num << 31) / w_denom + 1) >> 1);
      if (w < 0)
        w = 0;
      else if (w > (1 << 30))
        w = 1 << 30;
      image[i][j] = w;
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
    PNG_COLOR_TYPE_GRAY,
    PNG_INTERLACE_NONE,
    PNG_COMPRESSION_TYPE_BASE,
    PNG_FILTER_TYPE_BASE
  );

  png_write_info(png_ptr, info_ptr);

  png_byte pixels[376][361];
  for (int i = 0; i < 376; ++i)
    for (int j = 0; j < 361; ++j)
      pixels[i][j] = (png_byte)((image[i][j] * 255LL + (1 << 29)) >> 30);

  png_byte *rows[376];
  for (int i = 0; i < 376; ++i)
    rows[i] = pixels[i];

  png_write_image(png_ptr, rows);

  png_write_end(png_ptr, NULL);
  fclose(fp);

  return EXIT_SUCCESS;
}
