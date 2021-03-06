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

import mpmath
import numpy
import utils.yaml_io

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

mpmath.mp.prec = 106

#numpy.set_printoptions(threshold = numpy.inf)

if len(sys.argv) < 3:
  print(f'usage: {sys.argv[0]:s} mired_to_rgb_fit_in.yml device')
  sys.exit(EXIT_FAILURE)
mired_to_rgb_fit_in = sys.argv[1]
device = sys.argv[2]

mired_to_rgb_fit = utils.yaml_io._import(
  utils.yaml_io.read_file(mired_to_rgb_fit_in)
)
#a = mired_to_rgb_fit['a']
b_red = mired_to_rgb_fit['b_red']
b_green = mired_to_rgb_fit['b_green']
b_blue = mired_to_rgb_fit['b_blue']
c_blue = mired_to_rgb_fit['c_blue']
#d = mired_to_rgb_fit['d']
p_red_ab = mired_to_rgb_fit['p_red_ab']
#p_red_bd = mired_to_rgb_fit['p_red_bd']
p_green_ab = mired_to_rgb_fit['p_green_ab']
p_green_bd = mired_to_rgb_fit['p_green_bd']
#p_blue_ab = mired_to_rgb_fit['p_blue_ab']
p_blue_bc = mired_to_rgb_fit['p_blue_bc']
#p_blue_cd = mired_to_rgb_fit['p_blue_cd']

p_red_ab = numpy.array(p_red_ab, numpy.double)
p_green_ab = numpy.array(p_green_ab, numpy.double)
p_green_bd = numpy.array(p_green_bd, numpy.double)
p_blue_bc = numpy.array(p_blue_bc, numpy.double)

sys.stdout.write(
  sys.stdin.read().format(
    device = device,
    b_red = b_red,
    b_green = b_green,
    b_blue = b_blue,
    c_blue = c_blue,
    p_red_ab = ', '.join([f'{p_red_ab[i]:.8e}f' for i in range(p_red_ab.shape[0])]),
    p_green_ab = ', '.join([f'{p_green_ab[i]:.8e}f' for i in range(p_green_ab.shape[0])]),
    p_green_bd = ', '.join([f'{p_green_bd[i]:.8e}f' for i in range(p_green_bd.shape[0])]),
    p_blue_bc = ', '.join([f'{p_blue_bc[i]:.8e}f' for i in range(p_blue_bc.shape[0])])
  )
)
