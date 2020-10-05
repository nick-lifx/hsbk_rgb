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

def blackbody_spectra(kelv):
  return c1_on_lambda_5[:, numpy.newaxis] / (
    numpy.exp(c2_on_lambda[:, numpy.newaxis] / kelv[numpy.newaxis, :]) - 1.
  )

def blackbody_spectrum(kelv):
  return c1_on_lambda_5 / (numpy.exp(c2_on_lambda / kelv) - 1.)

if __name__ == '__main__':
  import ruamel.yaml
  from python_to_numpy import python_to_numpy
  yaml = ruamel.yaml.YAML(typ = 'safe')
  with open('standard_observer_2deg.yml') as fin:
    standard_observer_2deg = python_to_numpy(yaml.load(fin))
  XYZ = blackbody_spectrum(6504.) @ standard_observer_2deg
  xy = XYZ[:2] / numpy.sum(XYZ)
  print('xy', xy) # should be near (.31271, .32902)
