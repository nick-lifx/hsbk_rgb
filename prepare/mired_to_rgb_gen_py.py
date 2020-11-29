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

import numpy
import ruamel.yaml
import sys
from python_to_numpy import python_to_numpy

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

if len(sys.argv) < 3:
  print(f'usage: {sys.argv[0]:s} mired_to_rgb_fit_in.yml device')
  sys.exit(EXIT_FAILURE)
mired_to_rgb_fit_in = sys.argv[1]
device = sys.argv[2]

yaml = ruamel.yaml.YAML(typ = 'safe')
#numpy.set_printoptions(threshold = numpy.inf)

with open(mired_to_rgb_fit_in) as fin:
  mired_to_rgb_fit = python_to_numpy(yaml.load(fin))
a = mired_to_rgb_fit['a']
b_red = mired_to_rgb_fit['b_red']
b_green = mired_to_rgb_fit['b_green']
b_blue = mired_to_rgb_fit['b_blue']
c_blue = mired_to_rgb_fit['c_blue']
d = mired_to_rgb_fit['d']
p_red_ab = mired_to_rgb_fit['p_red_ab']
p_red_bd = mired_to_rgb_fit['p_red_bd']
p_green_ab = mired_to_rgb_fit['p_green_ab']
p_green_bd = mired_to_rgb_fit['p_green_bd']
p_blue_ab = mired_to_rgb_fit['p_blue_ab']
p_blue_bc = mired_to_rgb_fit['p_blue_bc']
p_blue_cd = mired_to_rgb_fit['p_blue_cd']

print(
  '''#!/usr/bin/env python3
# generated by ../prepare/mired_to_rgb_gen_py.py

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

import numpy

EPSILON = 1e-6

def mired_to_rgb_{0:s}(mired):
  # validate inputs, allowing a little slack
  assert mired >= {1:.16e} - EPSILON and mired < {2:.16e} + EPSILON

  # calculate red channel
  if mired < {3:.16e}:
    r = {4:.16e}
{5:s}  else:
    r = {6:.16e}
{7:s}
  # calculate green channel
  if mired < {8:.16e}:
    g = {9:.16e}
{10:s}  else:
    g = {11:.16e}
{12:s}
  # calculate blue channel
  if mired < {13:.16e}:
    b = {14:.16e}
{15:s}  elif mired < {16:.16e}:
    b = {17:.16e}
{18:s}  else:
    b = {19:.16e}
{20:s}
  return numpy.array([r, g, b], numpy.double)

if __name__ == '__main__':
  import sys

  EXIT_SUCCESS = 0
  EXIT_FAILURE = 1

  RGB_RED = 0
  RGB_GREEN = 1
  RGB_BLUE = 2
  N_RGB = 3

  if len(sys.argv) < 2:
    print(f'usage: {{sys.argv[0]:s}} mired')
    print('mired = colour temperature in micro reciprocal degrees Kelvin')
    sys.exit(EXIT_FAILURE)
  mired = float(sys.argv[1])

  rgb = mired_to_rgb_{21:s}(mired)
  print(
    f'mired {{mired:.3f}} -> RGB ({{rgb[RGB_RED]:.6f}}, {{rgb[RGB_GREEN]:.6f}}, {{rgb[RGB_BLUE]:.6f}})'
  )'''.format(
    device,
    a,
    d,
    b_red,
    p_red_ab[-1],
    ''.join(
      [
        '    r = r * mired + {0:.16e}\n'.format(p_red_ab[i])
        for i in range(p_red_ab.shape[0] - 2, -1, -1)
      ]
    ),
    p_red_bd[-1],
    ''.join(
      [
        '    r = r * mired + {0:.16e}\n'.format(p_red_bd[i])
        for i in range(p_red_bd.shape[0] - 2, -1, -1)
      ]
    ),
    b_green,
    p_green_ab[-1],
    ''.join(
      [
        '    g = g * mired + {0:.16e}\n'.format(p_green_ab[i])
        for i in range(p_green_ab.shape[0] - 2, -1, -1)
      ]
    ),
    p_green_bd[-1],
    ''.join(
      [
        '    g = g * mired + {0:.16e}\n'.format(p_green_bd[i])
        for i in range(p_green_bd.shape[0] - 2, -1, -1)
      ]
    ),
    b_blue,
    p_blue_ab[-1],
    ''.join(
      [
        '    b = b * mired + {0:.16e}\n'.format(p_blue_ab[i])
        for i in range(p_blue_ab.shape[0] - 2, -1, -1)
      ]
    ),
    c_blue,
    p_blue_bc[-1],
    ''.join(
      [
        '    b = b * mired + {0:.16e}\n'.format(p_blue_bc[i])
        for i in range(p_blue_bc.shape[0] - 2, -1, -1)
      ]
    ),
    p_blue_cd[-1],
    ''.join(
      [
        '    b = b * mired + {0:.16e}\n'.format(p_blue_cd[i])
        for i in range(p_blue_cd.shape[0] - 2, -1, -1)
      ]
    ),
    device
  )
)
