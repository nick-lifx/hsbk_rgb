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
