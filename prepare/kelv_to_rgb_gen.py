#!/usr/bin/env python3

import numpy
import os
import ruamel.yaml
import sys
from python_to_numpy import python_to_numpy

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

if len(sys.argv) < 3:
  print(f'usage: {sys.argv[0]:s} UVW_to_rgb_in.yml kelv_to_rgb_out.py [func_name]')
  sys.exit(EXIT_FAILURE)
UVW_to_rgb_in = sys.argv[1]
kelv_to_rgb_py_out = sys.argv[2]
func_name = sys.argv[3] if len(sys.argv) >= 4 else 'kelv_to_rgb'

yaml = ruamel.yaml.YAML(typ = 'safe')
#numpy.set_printoptions(threshold = numpy.inf)

with open(UVW_to_rgb_in) as fin:
  UVW_to_rgb = python_to_numpy(yaml.load(fin))

with open(kelv_to_rgb_py_out, 'w') as fout:
  fout.write(
    '''#!/usr/bin/env python3
# generated by prepare/kelv_to_rgb_gen.py

import numpy
from kelv_to_uv import kelv_to_uv

# this is precomputed for the particular primaries in use
UVW_to_rgb = numpy.array(
  [
    [{0:.15g}, {1:.15g}, {2:.15g}],
    [{3:.15g}, {4:.15g}, {5:.15g}],
    [{6:.15g}, {7:.15g}, {8:.15g}]
  ],
  numpy.double
)

def {9:s}(kelv):
  # find the approximate (u, v) chromaticity of the given Kelvin value
  uv = kelv_to_uv(kelv)
  
  # add the missing w, to convert the chromaticity from (u, v) to (U, V, W)
  # see https://en.wikipedia.org/wiki/CIE_1960_color_space
  u = uv[0]
  v = uv[1]
  UVW = numpy.array([u, v, 1. - u - v], numpy.double)
  
  # convert to rgb in the given system (the brightness will be arbitrary)
  rgb = UVW_to_rgb @ UVW
  
  # low Kelvins are outside the gamut of SRGB and thus must be interpreted,
  # in this simplistic approach we simply clip off the negative blue value
  rgb[rgb < 0.] = 0.
  
  # normalize the brightness, so that at least one of R, G, or B = 1
  rgb /= numpy.max(rgb)
  
  # gamma-encode the R, G, B tuple according to the SRGB gamma curve
  # because displaying it on a monitor will gamma-decode it in the process
  mask = rgb < .0031308
  rgb[mask] *= 12.92
  rgb[~mask] = 1.055 * rgb[~mask] ** (1. / 2.4) - 0.055

  return rgb

if __name__ == '__main__':
  import sys

  EXIT_SUCCESS = 0
  EXIT_FAILURE = 1

  RGB_RED = 0
  RGB_GREEN = 1
  RGB_BLUE = 2
  N_RGB = 3

  if len(sys.argv) < 2:
    print(f'usage: {{sys.argv[0]:s}} kelv')
    print('kelv = colour temperature in degrees Kelvin')
    sys.exit(EXIT_FAILURE)
  kelv = float(sys.argv[1])

  rgb = {10:s}(kelv)
  print(
    f'kelv {{kelv:.3f}} -> RGB ({{rgb[RGB_RED]:.6f}}, {{rgb[RGB_GREEN]:.6f}}, {{rgb[RGB_BLUE]:.6f}})'
  )
'''.format(
    UVW_to_rgb[0, 0],
    UVW_to_rgb[0, 1],
    UVW_to_rgb[0, 2],
    UVW_to_rgb[1, 0],
    UVW_to_rgb[1, 1],
    UVW_to_rgb[1, 2],
    UVW_to_rgb[2, 0],
    UVW_to_rgb[2, 1],
    UVW_to_rgb[2, 2],
    func_name,
    func_name
  )
)
