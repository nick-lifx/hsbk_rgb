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
#include "gamma_decode.h"
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

#define UV_u 0
#define UV_v 1
#define N_UV 2

#define UVW_U 0
#define UVW_V 1
#define UVW_W 2
#define N_UVW 3

#define EPSILON 1e-6f

// inverse of the matrix calculated by ../prepare/UVW_to_rgb.py
float rgb_to_UVW[N_UVW][N_RGB] = {
  {9.04510486e-02f, 7.84301651e-02f, 3.95854529e-02f},
  {6.99582329e-02f, 2.35290495e-01f, 2.37512718e-02f},
  {4.02789826e-02f, 3.13720660e-01f, 1.62300357e-01f}
};

void hsbk_to_uv(const float *hsbk, float *uv) {
  float rgb[N_RGB];
  hsbk_to_rgb(hsbk, rgb);

  for (int i = 0; i < N_RGB; ++i)
    rgb[i] = gamma_decode(rgb[i]);

  float UVW[N_UVW];
  for (int i = 0; i < N_UVW; ++i) {
    float v = 0.f;
    for (int j = 0; j < N_RGB; ++j)
      v += rgb_to_UVW[i][j] * rgb[j];
    UVW[i] = v;
  }

  float L = 0.f;
  for (int i = 0; i < N_UVW; ++i)
    L += UVW[i];
  uv[UV_u] = UVW[UVW_U] / L;
  uv[UV_v] = UVW[UVW_V] / L;
}

int main(int argc, char **argv) {
  if (argc < 2) {
    printf(
      "usage: %s image_out\n"
        "image_out = name of PNG file to create (will be overwritten)\n"
        "creates 361 x 376 x 3 image with 0..360 degrees by 1, 1500..9000 Kelvin by 20\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }
  char *image_out = argv[1];

  // find chromaticities of the hue space by 1 degree increments
  float hue_uv[361][N_UV];
  for (int i = 0; i < 361; ++i) {
    float hsbk[N_HSBK] = {1.f * i, 1.f, 1.f, 6504.f};
    hsbk_to_uv(hsbk, hue_uv[i]);
  }

  // find chromaticities of the Kelvin space by 20 degree increments
  float kelv_uv[376][N_UV];
  for (int i = 0; i < 376; ++i) {
    float hsbk[N_HSBK] = {0.f, 0.f, 1.f, 1500.f + 20.f * i};
    hsbk_to_uv(hsbk, kelv_uv[i]);
  }

  // find chromaticities of the hue x Kelvin space @ saturation .5, then
  // convert each chromaticity to a weighting between hue_uv and kelv_uv
  float image[376][361];
  for (int i = 0; i < 376; ++i) {
    //printf("%d / 376\n", i);
    float kelv = 1500.f + 20.f * i;
    float v0[N_UV] = {
      kelv_uv[i][UV_u],
      kelv_uv[i][UV_v]
    };
    for (int j = 0; j < 361; ++j) {
      float hue = 1.f * j;
      float v1[N_UV] = {
        hue_uv[j][UV_u] - v0[UV_u],
        hue_uv[j][UV_v] - v0[UV_v]
      };
      float hsbk[N_HSBK] = {hue, .5f, 1.f, kelv};
      float uv[N_UV];
      hsbk_to_uv(hsbk, uv);
      float w = (
        (uv[UV_u] - v0[UV_u]) * v1[UV_u] +
          (uv[UV_v] - v0[UV_v]) * v1[UV_v]
      ) / (
        v1[UV_u] * v1[UV_u] +
          v1[UV_v] * v1[UV_v]
      );
      if (w < 0.f)
        w = 0.f;
      else if (w > 1.f)
        w = 1.f;
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
      pixels[i][j] = (png_byte)roundf(image[i][j] * 255.f);

  png_byte *rows[376];
  for (int i = 0; i < 376; ++i)
    rows[i] = pixels[i];

  png_write_image(png_ptr, rows);

  png_write_end(png_ptr, NULL);
  fclose(fp);

  return EXIT_SUCCESS;
}
