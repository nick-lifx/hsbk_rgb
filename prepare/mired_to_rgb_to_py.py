#!/usr/bin/env python3

import numpy
import math
import os
import ruamel.yaml
import sys
from python_to_numpy import python_to_numpy

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

if len(sys.argv) < 3:
  print(f'usage: {sys.argv[0]:s} mired_to_rgb_fit_in.yml mired_to_rgb_out.py')
  sys.exit(EXIT_FAILURE)
mired_to_rgb_fit_in = sys.argv[1]
mired_to_rgb_py_out = sys.argv[2]

yaml = ruamel.yaml.YAML(typ = 'safe')
#numpy.set_printoptions(threshold = numpy.inf)

with open(mired_to_rgb_fit_in) as fin:
  mired_to_rgb_fit = python_to_numpy(yaml.load(fin))
mired_a = mired_to_rgb_fit['mired_a']
mired_b_red = mired_to_rgb_fit['mired_b_red']
mired_b_green = mired_to_rgb_fit['mired_b_green']
mired_b_blue = mired_to_rgb_fit['mired_b_blue']
mired_c = mired_to_rgb_fit['mired_c']
mired_d = mired_to_rgb_fit['mired_d']
p_red_ab = mired_to_rgb_fit['p_red_ab']
p_red_bd = mired_to_rgb_fit['p_red_bd']
p_green_ab = mired_to_rgb_fit['p_green_ab']
p_green_bd = mired_to_rgb_fit['p_green_bd']
p_blue_ab = mired_to_rgb_fit['p_blue_ab']
p_blue_bc = mired_to_rgb_fit['p_blue_bc']
p_blue_cd = mired_to_rgb_fit['p_blue_cd']

func_name = os.path.basename(mired_to_rgb_py_out)
assert func_name[-3:] == '.py'
func_name = func_name[:-3]
with open(mired_to_rgb_py_out, 'w') as fout:
  fout.write(
    '''#!/usr/bin/env python3
# generated by prepare/mired_to_rgb_to_py.py

import numpy

EPSILON = 1e-6

def {0:s}(mired):
  # validate inputs, allowing a little slack
  assert mired >= {1:.15g} - EPSILON
  assert mired < {2:.15g} + EPSILON

  # calculate red channel
  if mired < {3:.15g}:
    r = {4:.15g}
{5:s}  else:
    r = {6:.15g}
{7:s}
  # calculate green channel
  if mired < {8:.15g}:
    g = {9:.15g}
{10:s}  else:
    g = {11:.15g}
{12:s}
  # calculate blue channel
  if mired < {13:.15g}:
    b = {14:.15g}
{15:s}  elif mired < {16:.15g}:
    b = {17:.15g}
{18:s}  else:
    b = {19:.15g}
{20:s}
  return numpy.array([r, g, b], numpy.double)

if __name__ == '__main__':
  import sys

  EXIT_FAILURE = 1

  if len(sys.argv) < 2:
    print(f'usage: {{sys.argv[0]:s}} mired')
    print('mired = colour temperature in micro reciprocal degrees Kelvin')
    sys.exit(EXIT_FAILURE)
  mired = float(sys.argv[1])

  rgb = {21:s}(mired)
  print(
    f'mired {{mired:.3f}} -> RGB ({{rgb[0]:.6f}}, {{rgb[1]:.6f}}, {{rgb[2]:.6f}})'
  )
'''.format(
    func_name,
    mired_a,
    mired_d,
    mired_b_red,
    p_red_ab[-1],
    ''.join(
      [
        '    r = r * mired + {0:.15g}\n'.format(p_red_ab[i])
        for i in range(p_red_ab.shape[0] - 2, -1, -1)
      ]
    ),
    p_red_bd[-1],
    ''.join(
      [
        '    r = r * mired + {0:.15g}\n'.format(p_red_bd[i])
        for i in range(p_red_bd.shape[0] - 2, -1, -1)
      ]
    ),
    mired_b_green,
    p_green_ab[-1],
    ''.join(
      [
        '    g = g * mired + {0:.15g}\n'.format(p_green_ab[i])
        for i in range(p_green_ab.shape[0] - 2, -1, -1)
      ]
    ),
    p_green_bd[-1],
    ''.join(
      [
        '    g = g * mired + {0:.15g}\n'.format(p_green_bd[i])
        for i in range(p_green_bd.shape[0] - 2, -1, -1)
      ]
    ),
    mired_b_blue,
    p_blue_ab[-1],
    ''.join(
      [
        '    b = b * mired + {0:.15g}\n'.format(p_blue_ab[i])
        for i in range(p_blue_ab.shape[0] - 2, -1, -1)
      ]
    ),
    mired_c,
    p_blue_bc[-1],
    ''.join(
      [
        '    b = b * mired + {0:.15g}\n'.format(p_blue_bc[i])
        for i in range(p_blue_bc.shape[0] - 2, -1, -1)
      ]
    ),
    p_blue_cd[-1],
    ''.join(
      [
        '    b = b * mired + {0:.15g}\n'.format(p_blue_cd[i])
        for i in range(p_blue_cd.shape[0] - 2, -1, -1)
      ]
    ),
    func_name
  )
)
