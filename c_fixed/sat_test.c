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

#define EPSILON 1e-6

// inverse of the matrix calculated by ../prepare/UVW_to_rgb.py
int32_t rgb_to_UVW[N_UVW][N_RGB] = {
  {0xb93e664, 0xa09ffe9, 0x51122d9},
  {0x8f46431, 0x1e1dffbb, 0x30a481c},
  {0x527dc98, 0x2827ffa4, 0x14c64213}
};

void hsbk_to_uv(const int32_t *hsbk, int32_t *uv) {
  int32_t rgb[N_RGB];
  hsbk_to_rgb(hsbk, rgb);

  for (int i = 0; i < N_RGB; ++i)
    rgb[i] = gamma_decode(rgb[i]);

  int32_t UVW[N_UVW];
  for (int i = 0; i < N_UVW; ++i) {
    int64_t v = 1 << 29;
    for (int j = 0; j < N_RGB; ++j)
      v += (int64_t)rgb_to_UVW[i][j] * rgb[j];
    UVW[i] = (int32_t)(v >> 30);
  }

  int64_t L = 0;
  for (int i = 0; i < N_UVW; ++i)
    L += UVW[i];
  uv[UV_u] = (int32_t)((((int64_t)UVW[UVW_U] << 31) / L + 1) >> 1);
  uv[UV_v] = (int32_t)((((int64_t)UVW[UVW_V] << 31) / L + 1) >> 1);
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
  int32_t hue_uv[361][N_UV];
  for (int i = 0; i < 361; ++i) {
    int32_t hsbk[N_HSBK] = {
      (int32_t)((((int64_t)i << 33) / 360 + 1) >> 1),
      1 << 30,
      1 << 30,
      6504 << 16
    };
    hsbk_to_uv(hsbk, hue_uv[i]);
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
    hsbk_to_uv(hsbk, kelv_uv[i]);
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
      int32_t uv[N_UV];
      hsbk_to_uv(hsbk, uv);
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