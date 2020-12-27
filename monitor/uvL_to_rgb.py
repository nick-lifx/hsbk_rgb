#!/usr/bin/env python3

import numpy
import ruamel.yaml
import sys
from python_to_numpy import python_to_numpy

RGB_RED = 0
RGB_GREEN = 1
RGB_BLUE = 2
N_RGB = 3

UVL_u = 0
UVL_v = 1
UVL_L = 2
N_UVL = 3

UVW_U = 0
UVW_V = 1
UVW_W = 2
N_UVW = 3

if len(sys.argv) < 3:
  print(f'usage: {sys.argv[0]:s} model_in.yml u,v,L')
  sys.exit(1)
model_in = sys.argv[1]
uvL = numpy.array([float(i) for i in sys.argv[2].split(',')], numpy.double)

assert uvL.shape[0] == N_UVL

yaml = ruamel.yaml.YAML(typ = 'safe')
#numpy.set_printoptions(threshold = numpy.inf)

with open(model_in) as fin:
  model = python_to_numpy(yaml.load(fin))
gamma_a = model['gamma_a']
gamma_b = model['gamma_b']
gamma_c = model['gamma_c']
gamma_d = model['gamma_d']
gamma_e = model['gamma_e']
primaries_uvL = model['primaries_uvL']

# calculate normalized UVW vectors for the primaries
u = primaries_uvL[:, UVL_u]
v = primaries_uvL[:, UVL_v]
primaries_UVW = numpy.stack([u, v, 1. - u - v], 1)

# calculate UVW vector that we want to solve for
u = uvL[UVL_u]
v = uvL[UVL_v]
UVW = numpy.array([u, v, 1. - u - v], numpy.double) * uvL[UVL_L]

# calculate necessary L-value for each of the primaries
rgb0 = numpy.linalg.solve(
  primaries_UVW.transpose(),
  UVW
)

# gamma-encode
mask = rgb0 >= gamma_b
rgb1 = numpy.zeros_like(rgb0)
rgb1[~mask] = rgb0[~mask] * gamma_a
rgb1[mask] = (rgb0[mask] ** (1 / gamma_e) * gamma_d) - gamma_c

print(
  f'uvL ({uvL[UVL_u]:.6f}, {uvL[UVL_v]:.6f}, {uvL[UVL_L]:.6f}) -> rgb ({rgb1[RGB_RED]:.6f}, {rgb1[RGB_GREEN]:.6f}, {rgb1[RGB_BLUE]:.6f})'
)
