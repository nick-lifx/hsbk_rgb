#!/usr/bin/env python3
# generated by prepare/mired_to_rgb_gen.py

import numpy

EPSILON = 1e-6

def mired_to_rgb_srgb(mired):
  # validate inputs, allowing a little slack
  assert mired >= 66.6666666666667 - EPSILON
  assert mired < 1000 + EPSILON

  # calculate red channel
  if mired < 153.014204073907:
    r = 3.75228927004191e-09
    r = r * mired + 8.87539162481851e-06
    r = r * mired + 0.0012814326446354
    r = r * mired + 0.582677126816255
  else:
    r = 1

  # calculate green channel
  if mired < 153.389630135797:
    g = -3.1793151306219e-09
    g = g * mired + 5.60217181087732e-06
    g = g * mired + 0.00107609627512111
    g = g * mired + 0.691243100448387
  else:
    g = -2.89635036578811e-15
    g = g * mired + 7.50927775397408e-12
    g = g * mired + -8.13001567830012e-09
    g = g * mired + 5.12561863637464e-06
    g = g * mired + -0.00283237945006104
    g = g * mired + 1.31593131471919

  # calculate blue channel
  if mired < 152.740533596145:
    b = 1
  elif mired < 525.947680278181:
    b = -2.77865265294972e-18
    b = b * mired + 4.58804157412273e-15
    b = b * mired + -2.67958426105153e-12
    b = b * mired + 4.88020519177214e-10
    b = b * mired + 1.20547996848463e-07
    b = b * mired + -6.02756589897739e-05
    b = b * mired + 0.00420936766200165
    b = b * mired + 1.23798675622197
  else:
    b = 0

  return numpy.array([r, g, b], numpy.double)

if __name__ == '__main__':
  import sys

  EXIT_SUCCESS = 0
  EXIT_FAILURE = 1

  RGB_RED = 0
  RGB_GREEN = 1
  RGB_BLUE = 2
  N_RGB = 3

  if len(sys.argv) < 2:
    print(f'usage: {sys.argv[0]:s} mired')
    print('mired = colour temperature in micro reciprocal degrees Kelvin')
    sys.exit(EXIT_FAILURE)
  mired = float(sys.argv[1])

  rgb = mired_to_rgb_srgb(mired)
  print(
    f'mired {mired:.3f} -> RGB ({rgb[RGB_RED]:.6f}, {rgb[RGB_GREEN]:.6f}, {rgb[RGB_BLUE]:.6f})'
  )
