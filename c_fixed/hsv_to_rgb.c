#include <errno.h>
#include <math.h>
#include <png.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "hsbk_to_rgb.h"

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

#define EPSILON 1e-6

int main(int argc, char **argv) {
  if (argc < 3) {
    printf(
      "usage: %s image_in image_out [kelv]\n"
        "image_in = name of PNG file (HSV pixels) to read\n"
        "image_out = name of PNG file to create (will be overwritten)\n"
        "kelv = implicit colour temperature to apply to HSV pixels (default 6504K)\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }
  char *image_in = argv[1];
  char *image_out = argv[2];
  int32_t kelv =
    argc >= 4 ?
      (int32_t)roundf(ldexpf(atof(argv[3]), 16)) :
      (int32_t)6504 << 16;

  FILE *fp = fopen(image_in, "r");
  if (fp == NULL) {
    perror(image_in);
    exit(EXIT_FAILURE);
  }

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

  png_byte *pixels = malloc(size_y * size_x * N_HSV * sizeof(png_byte));
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
    rows[i] = pixels + i * size_x * N_HSV;

  png_read_image(png_ptr, rows);

  int32_t *image = malloc(size_y * size_x * N_HSV * sizeof(int32_t));
  if (image == NULL) {
    perror("malloc()");
    exit(EXIT_FAILURE);
  }
  for (int i = 0; i < size_y; ++i)
    for (int j = 0; j < size_x; ++j) {
      image[(i * size_x + j) * N_HSV + HSV_HUE] =
        pixels[(i * size_x + j) * N_HSV + HSV_HUE] << 24;
      image[(i * size_x + j) * N_HSV + HSV_SAT] = (uint32_t)(
        (
          (
            (int64_t)pixels[(i * size_x + j) * N_HSV + HSV_SAT] << 31
          ) / 255 + 1
        ) >> 1
      );
      image[(i * size_x + j) * N_HSV + HSV_VAL] = (uint32_t)(
        (
          (
            (int64_t)pixels[(i * size_x + j) * N_HSV + HSV_VAL] << 31
          ) / 255 + 1
        ) >> 1
      );
    }

  png_read_end(png_ptr, NULL);
  fclose(fp);

  for (int i = 0; i < size_y; ++i) {
    //printf("%d / %d\n", i, size_y);
    for (int j = 0; j < size_x; ++j) {
      int32_t hsbk[N_HSBK] = {0, 0, 0, kelv};
      memcpy(
        hsbk,
        image + (i * size_x + j) * N_RGB,
        N_HSV * sizeof(int32_t)
      );
      hsbk_to_rgb(hsbk, image + (i * size_x + j) * N_RGB);
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
    for (int j = 0; j < size_x; ++j)
      for (int k = 0; k < N_RGB; ++k)
        pixels[(i * size_x + j) * N_RGB + k] = (png_byte)(
          (image[(i * size_x + j) * N_RGB + k] * 255LL + (1 << 29)) >> 30
        );
  free(image);

  png_write_image(png_ptr, rows);

  free(pixels);
  free(rows);

  png_write_end(png_ptr, NULL);
  fclose(fp);

  return EXIT_SUCCESS;
}