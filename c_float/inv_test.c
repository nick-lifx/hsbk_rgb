#include <assert.h>
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

#define EPSILON 1e-6

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
  float kelv = argc >= 4 ? atof(argv[3]) : 0.f;

  srand(seed);
  for (int i = 0; i < count; ++i) {
    float rgb[N_RGB];
    for (int j = 0; j < N_RGB; ++j)
      rgb[j] = (float)rand() / RAND_MAX;
    float hsbk[N_HSBK];
    rgb_to_hsbk(rgb, kelv, hsbk);
    float rgb1[N_RGB];
    hsbk_to_rgb(hsbk, rgb);
    for (int j = 0; j < N_RGB; ++j)
      assert(abs(rgb1[j] - rgb[j]) < EPSILON);
  }

  return EXIT_SUCCESS;
}
