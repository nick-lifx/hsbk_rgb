#!/usr/bin/env python3

import math
import numpy
import ruamel.yaml
import sys
from blackbody_spectrum import blackbody_spectrum
from numpy_to_python import numpy_to_python
from python_to_numpy import python_to_numpy

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

UVW_U = 0
UVW_V = 1
UVW_W = 2
N_UVW = 3

XYZ_X = 0
XYZ_Y = 1
XYZ_Z = 2
N_XYZ = 3

# see https://en.wikipedia.org/wiki/CIE_1960_color_space
XYZ_to_UVW = numpy.array(
  [
    [2. / 3., 0., 0.],
    [0., 1., 0.],
    [-1. / 2., 3. / 2, 1. / 2.]
  ],
  numpy.double
)

EPSILON = 1e-6

# 281 data points in the range 66.667~1000 mireds with spacing 3.333
MIRED_A = 1e6 / 15000.
MIRED_B = 1e6 / 1000.
N_MIRED = 281

if len(sys.argv) < 2:
  print(f'usage: {sys.argv[0]:s} mired_to_uv_data_out.yml')
  sys.exit(EXIT_FAILURE)
mired_to_uv_data_out = sys.argv[1]

yaml = ruamel.yaml.YAML(typ = 'safe')
#numpy.set_printoptions(threshold = numpy.inf)

with open('standard_observer_2deg.yml') as fin:
  standard_observer_2deg = python_to_numpy(yaml.load(fin))

# prepare mired scale
mired_scale = numpy.linspace(MIRED_A, MIRED_B, N_MIRED)

# prepare data points
XYZ = numpy.stack(
  [
    blackbody_spectrum(1e6 / mired_scale[i]) @ standard_observer_2deg
    for i in range(N_MIRED)
  ],
  0
)
UVW = (XYZ_to_UVW @ XYZ.transpose()).transpose()
data_points = UVW[:, :UVW_W] / numpy.sum(UVW, 1)[:, numpy.newaxis]

# write scale and data points for fitting
mired_to_uv_data = {
  'mired_scale': mired_scale,
  'data_points': data_points
}
with open(mired_to_uv_data_out, 'w') as fout:
  yaml.dump(numpy_to_python(mired_to_uv_data), fout)
