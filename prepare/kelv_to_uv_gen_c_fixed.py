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
from utils.poly_fixed import poly_fixed
from utils.to_fixed import to_fixed
from utils.to_hex import to_hex

EPSILON = 1e-6

mpmath.mp.prec = 106

# independent variable in 16:16 fixed point
KELV_EXP = -16
KELV_MIN = 1000.
KELV_MAX = 15000.

# results in 2:30 fixed point
UV_EXP = -30

p_u_num, p_u_num_shr, p_exp_u_num = poly_fixed(
  mpmath.matrix([.860117757, 1.54118254e-4, 1.28641212e-7]),
  KELV_MIN,
  KELV_MAX,
  KELV_EXP,
  31
)
p_u_denom, p_u_denom_shr, p_exp_u_denom = poly_fixed(
  mpmath.matrix([1., 8.42420235e-4, 7.08145163e-7]),
  KELV_MIN,
  KELV_MAX,
  KELV_EXP,
  31
)
p_v_num, p_v_num_shr, p_exp_v_num = poly_fixed(
  mpmath.matrix([.317398726, 4.22806245e-5, 4.20481691e-8]),
  KELV_MIN,
  KELV_MAX,
  KELV_EXP,
  31
)
p_v_denom, p_v_denom_shr, p_exp_v_denom = poly_fixed(
  mpmath.matrix([1., -2.89741816e-5, 1.61456053e-7]),
  KELV_MIN,
  KELV_MAX,
  KELV_EXP,
  31
)

# make sure we can divide u_num by u_denom and v_num by v_denom
# maximum we can shift by is 32, but allow one less for rounding
div_shl_u = p_exp_u_num[0] - p_exp_u_denom[0] - UV_EXP
assert div_shl_u >= 0 and div_shl_u < 32
div_shl_v = p_exp_v_num[0] - p_exp_v_denom[0] - UV_EXP
assert div_shl_v >= 0 and div_shl_v < 32

sys.stdout.write(
  sys.stdin.read().format(
    kelv_min = to_fixed(KELV_MIN * (1. - EPSILON), KELV_EXP),
    kelv_max = to_fixed(KELV_MAX * (1. + EPSILON), KELV_EXP),
    p_u_num2 = to_hex(p_u_num[2]),
    p_u_num1 = to_hex(p_u_num[1]),
    p_u_num_shr1 = p_u_num_shr[1],
    p_u_num0 = to_hex(p_u_num[0]),
    p_u_num_shr0 = p_u_num_shr[0],
    p_u_denom2 = to_hex(p_u_denom[2]),
    p_u_denom1 = to_hex(p_u_denom[1]),
    p_u_denom_shr1 = p_u_denom_shr[1],
    p_u_denom0 = to_hex(p_u_denom[0]),
    p_u_denom_shr0 = p_u_denom_shr[0],
    div_shl_u_plus_one = div_shl_u + 1,
    p_v_num2 = to_hex(p_v_num[2]),
    p_v_num1 = to_hex(p_v_num[1]),
    p_v_num_shr1 = p_v_num_shr[1],
    p_v_num0 = to_hex(p_v_num[0]),
    p_v_num_shr0 = p_v_num_shr[0],
    p_v_denom2 = to_hex(p_v_denom[2]),
    minus_p_v_denom1 = to_hex(-p_v_denom[1]),
    p_v_denom_shr1 = p_v_denom_shr[1],
    p_v_denom0 = to_hex(p_v_denom[0]),
    p_v_denom_shr0 = p_v_denom_shr[0],
    div_shl_v_plus_one = div_shl_v + 1
  )
)
