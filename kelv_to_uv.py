#!/usr/bin/env python3

import math
import numpy
import sys

EPSILON = 1e-6

def kelv_to_uv(kelv):
  # validate inputs, allowing a little slack
  assert kelv >= 1000. - EPSILON and kelv < 15000. + EPSILON

  # find the approximate (u, v) chromaticity of the given Kelvin value
  # see http://en.wikipedia.org/wiki/Planckian_locus#Approximation (Krystek)
  # we evaluate this with Horner's rule for better numerical stability
  u = (
    ((1.28641212e-7 * kelv + 1.54118254e-4) * kelv + .860117757) /
      ((7.08145163e-7 * kelv + 8.42420235e-4) * kelv + 1.)
  )
  v = (
    ((4.20481691e-8 * kelv + 4.22806245e-5) * kelv + .317398726) /
      ((1.61456053e-7 * kelv - 2.89741816e-5) * kelv + 1.)
  )

  return numpy.array([u, v], numpy.double)

if __name__ == '__main__':
  import sys

  EXIT_FAILURE = 1

  if len(sys.argv) < 2:
    print(f'usage: {sys.argv[0]:s} kelv')
    print('kelv = colour temperature in degrees Kelvin')
    sys.exit(EXIT_FAILURE)
  kelv = float(sys.argv[1])

  uv = kelv_to_uv(kelv)
  print(
    f'kelv {kelv:.3f} -> uv ({uv[0]:.6f}, {uv[1]:.6f})'
  )
