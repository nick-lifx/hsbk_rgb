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
  u = 1.28641212e-7
  u = u * kelv + 1.54118254e-4
  u = u * kelv + .860117757
  u_denom = 7.08145163e-7
  u_denom = u_denom * kelv + 8.42420235e-4
  u_denom = u_denom * kelv + 1.
  u /= u_denom

  v = 4.20481691e-8
  v = v * kelv + 4.22806245e-5
  v = v * kelv + .317398726
  v_denom = 1.61456053e-7
  v_denom = v_denom * kelv - 2.89741816e-5
  v_denom = v_denom * kelv + 1.
  v /= v_denom

  return numpy.array([u, v], numpy.double)

if __name__ == '__main__':
  import sys

  EXIT_SUCCESS = 0
  EXIT_FAILURE = 1

  UV_u = 0
  UV_v = 1
  N_UV = 2

  if len(sys.argv) < 2:
    print(f'usage: {sys.argv[0]:s} kelv')
    print('kelv = colour temperature in degrees Kelvin')
    sys.exit(EXIT_FAILURE)
  kelv = float(sys.argv[1])

  uv = kelv_to_uv(kelv)
  print(
    f'kelv {kelv:.3f} -> uv ({uv[UV_u]:.6f}, {uv[UV_v]:.6f})'
  )