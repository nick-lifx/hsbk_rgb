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

# put utils into path
# temporary until we have proper Python packaging
import os.path
import sys
dirname = os.path.dirname(__file__)
sys.path.append(os.path.join(dirname, '..'))

import math
import numpy

CONST_h = 6.62607015e-34 # Planck's constant
CONST_c = 299792458. # speed of light
CONST_k = 1.380649e-23 # Boltzmann's constant
CONST_c1 = 2. * math.pi * CONST_h * CONST_c ** 2
CONST_c2 = CONST_h * CONST_c / CONST_k

standard_observer_lambda = numpy.linspace(360e-9, 830e-9, 471, numpy.double)

c1_on_lambda_5 = CONST_c1 / standard_observer_lambda ** 5
c2_on_lambda = CONST_c2 / standard_observer_lambda
def blackbody_spectrum_multi(kelv):
  return c1_on_lambda_5[numpy.newaxis, :] / (
    numpy.exp(c2_on_lambda[numpy.newaxis, :] / kelv[:, numpy.newaxis]) - 1.
  )

def blackbody_spectrum(kelv):
  return blackbody_spectrum_multi(
    numpy.array([kelv], numpy.double)
  )[0, :]

c1_c2_on_lambda_6 = CONST_c1 * CONST_c2 / standard_observer_lambda ** 6
c2_on_lambda = CONST_c2 / standard_observer_lambda
def blackbody_spectrum_deriv_multi(kelv):
  e = numpy.exp(c2_on_lambda[numpy.newaxis, :] / kelv[:, numpy.newaxis])
  return c1_c2_on_lambda_6[numpy.newaxis, :] * e / (
    (kelv[:, numpy.newaxis] * (e - 1.)) ** 2
  )

def blackbody_spectrum_deriv(kelv):
  return blackbody_spectrum_deriv_multi(
    numpy.array([kelv], numpy.double)
  )[0, :]

if __name__ == '__main__':
  import utils.yaml_io

  standard_observer_2deg = utils.yaml_io._import(
    utils.yaml_io.read_file(
      os.path.join(dirname, 'standard_observer_2deg.yml')
    )
  )

  XYZ = blackbody_spectrum(6504.) @ standard_observer_2deg
  xy = XYZ[:2] / numpy.sum(XYZ)
  print('xy', xy) # should be near (.31271, .32902)

  XYZ = blackbody_spectrum_deriv(6504.) @ standard_observer_2deg
  XYZ0 = blackbody_spectrum(6504.) @ standard_observer_2deg
  XYZ1 = blackbody_spectrum(6504.001) @ standard_observer_2deg
  print('XYZ', XYZ, (XYZ1 - XYZ0) / .001)
