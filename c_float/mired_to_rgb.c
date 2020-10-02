#include <assert.h>
#include "mired_to_rgb.h"

#define RGB_RED 0
#define RGB_GREEN 1
#define RGB_BLUE 2
#define N_RGB 3

#define EPSILON 1e-6

void mired_to_rgb(float mired, float *rgb) {
  // validate inputs, allowing a little slack
  assert(mired >= 66.6666666666667 - EPSILON);
  assert(mired < 1000 + EPSILON);

  // calculate red channel
  float r;
  if (mired < 153.014204073907f) {
    r = 3.75228927004191e-09f;
    r = r * mired + 8.87539162481851e-06f;
    r = r * mired + 0.0012814326446354f;
    r = r * mired + 0.582677126816255f;
  }
  else {
    r = 1.f;
  }

  // calculate green channel
  float g;
  if (mired < 153.389630135797f) {
    g = -3.1793151306219e-09f;
    g = g * mired + 5.60217181087732e-06f;
    g = g * mired + 0.00107609627512111f;
    g = g * mired + 0.691243100448387f;
  }
  else {
    g = -2.89635036578811e-15f;
    g = g * mired + 7.50927775397408e-12f;
    g = g * mired + -8.13001567830012e-09f;
    g = g * mired + 5.12561863637464e-06f;
    g = g * mired + -0.00283237945006104f;
    g = g * mired + 1.31593131471919f;
  }

  // calculate blue channel
  float b;
  if (mired < 152.740533596145f) {
    b = 1.f;
  }
  else if (mired < 525.947680278181f) {
    b = -2.77865265294972e-18f;
    b = b * mired + 4.58804157412273e-15f;
    b = b * mired + -2.67958426105153e-12f;
    b = b * mired + 4.88020519177214e-10f;
    b = b * mired + 1.20547996848463e-07f;
    b = b * mired + -6.02756589897739e-05f;
    b = b * mired + 0.00420936766200165f;
    b = b * mired + 1.23798675622197f;
  }
  else {
    b = 0.f;
  }

  rgb[RGB_RED] = r;
  rgb[RGB_GREEN] = g;
  rgb[RGB_BLUE] = b;
}

#ifdef STANDALONE
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv) {
  if (argc < 2) {
    printf(
      "usage: %s mired\n"
        "mired = colour temperature in micro reciprocal degrees Kelvin\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }
  float mired = atof(argv[1]);

  float rgb[N_RGB];
  mired_to_rgb(mired, rgb);
  printf(
    "mired %.3f -> RGB (%.6f, %.6f, %.6f)\n",
    mired,
    rgb[RGB_RED],
    rgb[RGB_GREEN],
    rgb[RGB_BLUE]
  );

  return EXIT_SUCCESS;
}
#endif
