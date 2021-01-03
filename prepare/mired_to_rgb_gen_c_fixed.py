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
import mpmath
import numpy
import utils.yaml_io
from utils.poly_fixed import poly_fixed

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

# independent variable in 16:16 fixed point
MIRED_EXP = -16

# results in 2:30 fixed point
RGB_EXP = -30

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
a = mired_to_rgb_fit['a']
b_red = mired_to_rgb_fit['b_red']
b_green = mired_to_rgb_fit['b_green']
b_blue = mired_to_rgb_fit['b_blue']
c_blue = mired_to_rgb_fit['c_blue']
d = mired_to_rgb_fit['d']
p_red_ab = mired_to_rgb_fit['p_red_ab']
#p_red_bd = mired_to_rgb_fit['p_red_bd']
p_green_ab = mired_to_rgb_fit['p_green_ab']
p_green_bd = mired_to_rgb_fit['p_green_bd']
#p_blue_ab = mired_to_rgb_fit['p_blue_ab']
p_blue_bc = mired_to_rgb_fit['p_blue_bc']
#p_blue_cd = mired_to_rgb_fit['p_blue_cd']

p_red_ab, p_red_ab_shr, _ = poly_fixed(
  p_red_ab,
  a,
  b_red,
  MIRED_EXP,
  31,
  RGB_EXP
)
p_green_ab, p_green_ab_shr, _ = poly_fixed(
  p_green_ab,
  a,
  b_green,
  MIRED_EXP,
  31,
  RGB_EXP
)
p_green_bd, p_green_bd_shr, _ = poly_fixed(
  p_green_bd,
  b_green,
  d,
  MIRED_EXP,
  31,
  RGB_EXP
)
p_blue_bc, p_blue_bc_shr, _ = poly_fixed(
  p_blue_bc,
  b_blue,
  c_blue,
  MIRED_EXP,
  31,
  RGB_EXP
)

def to_hex(x):
  return '{0:s}0x{1:x}'.format('' if x >= 0 else '-', abs(x))
print(
  '''// generated by ../prepare/mired_to_rgb_gen_c_fixed.py

// Copyright (c) 2020 Nick Downing
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to
// deal in the Software without restriction, including without limitation the
// rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
// sell copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
// IN THE SOFTWARE.

#include "mired_to_rgb_{0:s}.h"

const struct mired_to_rgb mired_to_rgb_{1:s} = {{
  {2:s},
  {3:s},
  {4:s},
  {5:s},
  {{{6:s}}},
  {{{7:s}}},
  {{{8:s}}},
  {{{9:s}}},
  {{{10:s}}},
  {{{11:s}}},
  {{{12:s}}},
  {{{13:s}}}
}};

#ifdef STANDALONE
int mired_to_rgb_standalone(
  const struct mired_to_rgb *context,
  int argc,
  char **argv
);
 
int main(int argc, char **argv) {{
  return mired_to_rgb_standalone(&mired_to_rgb_{14:s}, argc, argv);
}}
#endif'''.format(
    device,
    device,
    to_hex(int(round(math.ldexp(b_red, -MIRED_EXP)))),
    to_hex(int(round(math.ldexp(b_green, -MIRED_EXP)))),
    to_hex(int(round(math.ldexp(b_blue, -MIRED_EXP)))),
    to_hex(int(round(math.ldexp(c_blue, -MIRED_EXP)))),
    ', '.join([to_hex(p_red_ab[i]) for i in range(p_red_ab.shape[0])]),
    ', '.join([to_hex(p_green_ab[i]) for i in range(p_green_ab.shape[0])]),
    ', '.join([to_hex(p_green_bd[i]) for i in range(p_green_bd.shape[0])]),
    ', '.join([to_hex(p_blue_bc[i]) for i in range(p_blue_bc.shape[0])]),
    ', '.join([str(p_red_ab_shr[i]) for i in range(p_red_ab_shr.shape[0])]),
    ', '.join([str(p_green_ab_shr[i]) for i in range(p_green_ab_shr.shape[0])]),
    ', '.join([str(p_green_bd_shr[i]) for i in range(p_green_bd_shr.shape[0])]),
    ', '.join([str(p_blue_bc_shr[i]) for i in range(p_blue_bc_shr.shape[0])]),
    device
  )
)
