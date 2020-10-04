#include <assert.h>
#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include "hsbk_to_rgb.h"
#include "rgb_to_hsbk.h"

#define RGB_RED 0
#define RGB_GREEN 1
#define RGB_BLUE 2
#define N_RGB 3

#define HSBK_HUE 0
#define HSBK_SAT 1
#define HSBK_BR 2
#define HSBK_KELV 3
#define N_HSBK 4

#define EPSILON 0x400

int main(int argc, char **argv) {
  if (argc < 3) {
    printf(
      "usage: %s seed count [kelv]\n"
        "checks invertibility of the RGB -> HSBK -> RGB pipeline\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }
  int seed = atoi(argv[1]);
  int count = atoi(argv[2]);
  int32_t kelv =
    argc >= 4 ? (int32_t)roundf(ldexpf(atof(argv[3]), 16)) : (int32_t)0;

  srand(seed);
  for (int i = 0; i < count; ++i) {
    int32_t rgb[N_RGB];
    for (int j = 0; j < N_RGB; ++j)
      rgb[j] = ((int64_t)rand() << 30) / RAND_MAX;
 printf("%f %f %f\n", ldexpf(rgb[0], -30), ldexpf(rgb[1], -30), ldexpf(rgb[2], -30));
    int32_t hsbk[N_HSBK];
    rgb_to_hsbk(rgb, kelv, hsbk);
    int32_t rgb1[N_RGB];
    hsbk_to_rgb(hsbk, rgb1);
    for (int j = 0; j < N_RGB; ++j) {
      printf("%x %x %x -> %x %x %x\n", rgb1[0], rgb1[1], rgb1[2], rgb[0], rgb[1], rgb[2]);
      assert(abs(rgb1[j] - rgb[j]) < EPSILON);
    }
  }

  return EXIT_SUCCESS;
}
