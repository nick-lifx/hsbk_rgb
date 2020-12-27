#!/usr/bin/env python3

# Copyright (c) 2020 Nick Downing
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# determine where to load standard_observer_2deg.yml from
import os.path
dirname = os.path.dirname(__file__)

import blackbody_spectrum
import numpy
import ruamel.yaml
from python_to_numpy import python_to_numpy

UVW_U = 0
UVW_V = 1
UVW_W = 2
N_UVW = 3

# see https://en.wikipedia.org/wiki/CIE_1960_color_space
XYZ_to_UVW = numpy.array(
  [
    [2. / 3., 0., 0.],
    [0., 1., 0.],
    [-1. / 2., 3. / 2, 1. / 2.]
  ],
  numpy.double
)

yaml = ruamel.yaml.YAML(typ = 'safe')
with open(os.path.join(dirname, 'standard_observer_2deg.yml')) as fin:
  standard_observer_2deg = python_to_numpy(yaml.load(fin))

def mired_to_uv_multi(mired):
  UVW = numpy.einsum(
    'ij,jk,lk->il',
    blackbody_spectrum.blackbody_spectrum_multi(1e6 / mired),
    standard_observer_2deg,
    XYZ_to_UVW
  )
  return UVW[:, :UVW_W] / numpy.sum(UVW, 1)[:, numpy.newaxis]

def mired_to_uv(mired):
  return mired_to_uv_multi(
    numpy.array([mired], numpy.double)
  )[0, :]

def mired_to_uv_deriv_multi(mired):
  UVW = numpy.einsum(
    'ij,jk,lk->il',
    blackbody_spectrum.blackbody_spectrum_multi(1e6 / mired),
    standard_observer_2deg,
    XYZ_to_UVW
  )
  L = numpy.sum(UVW, 1)
  # chain rule
  # let y = f(1e6 / x) = f(u) where u = 1e6 / x, du/dx = -1e6 / x^2
  # dy/dx = df/du du/dx = -1e6 f'(1 / x) / x^2
  UVW_deriv = -1e6 * numpy.einsum(
    'ij,jk,lk->il',
    blackbody_spectrum.blackbody_spectrum_deriv_multi(1e6 / mired),
    standard_observer_2deg,
    XYZ_to_UVW
  ) / (mired ** 2)[:, numpy.newaxis]
  L_deriv = numpy.sum(UVW_deriv, 1)
  # quotient rule
  return (
    UVW_deriv[:, :UVW_W] * L[:, numpy.newaxis] -
      UVW[:, :UVW_W] * L_deriv[:, numpy.newaxis]
  ) / (L ** 2)[:, numpy.newaxis]

def mired_to_uv_deriv(mired):
  return mired_to_uv_deriv_multi(
    numpy.array([mired], numpy.double)
  )[0, :]

if __name__ == '__main__':
  print(mired_to_uv(1e6 / 6504.))

  uv = mired_to_uv_deriv(1e6 / 6504.)
  uv0 = mired_to_uv(1e6 / 6504.)
  uv1 = mired_to_uv((1e6 / 6504.) + .001)
  print('uv', uv, (uv1 - uv0) / .001)
