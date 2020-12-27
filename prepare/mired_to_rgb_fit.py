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
import math
import mired_to_uv
import poly
import ruamel.yaml
import sys
from any_f_to_poly import any_f_to_poly
from numpy_to_python import numpy_to_python
from python_to_numpy import python_to_numpy
from remez import remez

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

RGB_RED = 0
RGB_GREEN = 1
RGB_BLUE = 2
N_RGB = 3

UV_u = 0
UV_v = 1
N_UV = 2

UVL_u = 0
UVL_v = 1
UVL_L = 2
N_UVL = 3

ERR_ORDER = 18

# approximation order can be set separately for each channel and interval
ORDER_RED_AB = 4
ORDER_GREEN_AB = 4
ORDER_GREEN_BD = 6
ORDER_BLUE_BC = 8

# user has to provide an estimate of the red/blue and blue/zero intersection
# we will search for the actual intersection at user's estimate +/- this value
INTERSECT_EXTRA_DOMAIN = 100.

# we can fit a small extra region around the needed one
# tries to place a zero near each end of the region, allowing better joining
FIT_EXTRA_DOMAIN = 5.

# fit will be valid in this range
MIRED_MIN = 1e6 / 15000.
MIRED_MAX = 1e6 / 1000.

EPSILON = 1e-48

diag = False
if len(sys.argv) >= 2 and sys.argv[1] == '--diag':
  diag = True
  del sys.argv[1]
if len(sys.argv) < 5:
  print(f'usage: {sys.argv[0]:s} [--diag] model_in.yml b_estimate c_estimate mired_to_rgb_fit_out.yml')
  sys.exit(EXIT_FAILURE)
model_in = sys.argv[1]
b_estimate = float(sys.argv[2])
c_estimate = float(sys.argv[3])
mired_to_rgb_fit_out = sys.argv[4]

yaml = ruamel.yaml.YAML(typ = 'safe')
#numpy.set_printoptions(threshold = numpy.inf)

with open(model_in) as fin:
  model = python_to_numpy(yaml.load(fin))
gamma_a = model['gamma_a']
gamma_b = model['gamma_b']
gamma_c = model['gamma_c']
gamma_d = model['gamma_d']
gamma_e = model['gamma_e']
primaries_uvL = model['primaries_uvL']

def gamma_encode(x):
  y = numpy.zeros_like(x)
  mask = x >= gamma_b
  y[~mask] = x[~mask] * gamma_a
  y[mask] = x[mask] ** (1. / gamma_e) * gamma_d - gamma_c
  return y

u = primaries_uvL[:, UVL_u]
v = primaries_uvL[:, UVL_v]
L = primaries_uvL[:, UVL_L]
primaries_UVW = numpy.stack([u, v, 1. - u - v], 1) * L[:, numpy.newaxis]
 
# note: below is transposed so use rgb @ UVW_to_rgb, not UVW_to_rgb @ rgb
UVW_to_rgb = numpy.linalg.inv(primaries_UVW)
def mired_to_rgb(mired):
  mired_uv = mired_to_uv.mired_to_uv_multi(mired)

  u = mired_uv[:, UV_u]
  v = mired_uv[:, UV_v]
  mired_UVW = numpy.stack([u, v, 1. - u - v], 1)

  return mired_UVW @ UVW_to_rgb

# mired scale must meet the following specification:
#   a <= x <= b: blue is at 1, red and green are increasing
#   b <= x <= c: red is at 1, blue and green are decreasing
#   c <= x <= d: red is at 1, blue is at 0, green is decreasing
# where [a, d] is the domain, e.g. [1e6 / 15000, 1e6 / 1000]

a = MIRED_MIN
print('a', a)
d = MIRED_MAX
print('d', d)

# find b, i.e. where red meets blue
def f(x):
  mired_rgb = mired_to_rgb(x)
  return mired_rgb[:, RGB_RED] - mired_rgb[:, RGB_BLUE]
b = poly.newton(
  any_f_to_poly(
    f,
    b_estimate - INTERSECT_EXTRA_DOMAIN,
    b_estimate + INTERSECT_EXTRA_DOMAIN,
    ERR_ORDER
  ),
  b_estimate
)
print('b', b)

# find c, d, i.e. where blue meets 0
def f(x):
  mired_rgb = mired_to_rgb(x)
  return mired_rgb[:, RGB_BLUE]
c = (
  poly.newton(
    any_f_to_poly(
      f,
      c_estimate - INTERSECT_EXTRA_DOMAIN,
      c_estimate + INTERSECT_EXTRA_DOMAIN,
      ERR_ORDER
    ),
    c_estimate
  )
if c_estimate < MIRED_MAX else
  MIRED_MAX
)
print('c', c)

# red channel
def f(x):
  mired_rgb = mired_to_rgb(x)
  return gamma_encode(mired_rgb[:, RGB_RED] / mired_rgb[:, RGB_BLUE])
p_red_ab, _, p_red_ab_err = remez(
  f,
  a - FIT_EXTRA_DOMAIN,
  b + FIT_EXTRA_DOMAIN,
  ORDER_RED_AB,
  ERR_ORDER,
  epsilon = EPSILON
)
print('p_red_ab', p_red_ab)
print('p_red_ab_err', p_red_ab_err)
p_red_bd = numpy.array([1.], numpy.double)
p_red_bd_err = 0.

# green channel
def f(x):
  mired_rgb = mired_to_rgb(x)
  return gamma_encode(mired_rgb[:, RGB_GREEN] / mired_rgb[:, RGB_BLUE])
p_green_ab, _, p_green_ab_err = remez(
  f,
  a - FIT_EXTRA_DOMAIN,
  b + FIT_EXTRA_DOMAIN,
  ORDER_GREEN_AB,
  ERR_ORDER,
  epsilon = EPSILON
)
print('p_green_ab', p_green_ab)
print('p_green_ab_err', p_green_ab_err)
def f(x):
  mired_rgb = mired_to_rgb(x)
  return gamma_encode(mired_rgb[:, RGB_GREEN] / mired_rgb[:, RGB_RED])
p_green_bd, _, p_green_bd_err = remez(
  f,
  b - FIT_EXTRA_DOMAIN,
  d + FIT_EXTRA_DOMAIN,
  ORDER_GREEN_BD,
  ERR_ORDER,
  epsilon = EPSILON
)
print('p_green_bd', p_green_bd)
print('p_green_bd_err', p_green_bd_err)

# blue channel
p_blue_ab = numpy.array([1.], numpy.double)
p_blue_ab_err = 0.
def f(x):
  mired_rgb = mired_to_rgb(x)
  return gamma_encode(mired_rgb[:, RGB_BLUE] / mired_rgb[:, RGB_RED])
p_blue_bc, _, p_blue_bc_err = remez(
  f,
  b - FIT_EXTRA_DOMAIN,
  c + FIT_EXTRA_DOMAIN,
  ORDER_BLUE_BC,
  ERR_ORDER,
  epsilon = EPSILON
)
print('p_blue_bc', p_blue_bc)
print('p_blue_bc_err', p_blue_bc_err)
p_blue_cd = numpy.array([0.], numpy.double)
p_blue_cd_err = 0.

# fix discontinuities by setting b, c, d to exact intersections after fitting
b_red = poly.newton(poly.add(p_red_ab, -p_red_bd), b)
print('b_red', b_red)
b_green = poly.newton(poly.add(p_green_ab, -p_green_bd), b)
print('b_green', b_green)
b_blue = poly.newton(poly.add(p_blue_ab, -p_blue_bc), b)
print('b_blue', b_blue)
c_blue = (
  poly.newton(poly.add(p_blue_bc, -p_blue_cd), c)
if c < MIRED_MAX else
  MIRED_MAX
)
print('c_blue', c_blue)

if diag:
  import matplotlib.pyplot

  # ideal
  x_ab = numpy.linspace(a, b, 1000, numpy.double)
  x_bd = numpy.linspace(b, d, 1000, numpy.double)
  x = numpy.concatenate([x_ab, x_bd], 0)
  for i in range(N_RGB):
    def f_ab(x):
      mired_rgb = mired_to_rgb(x)
      return gamma_encode(mired_rgb[:, i] / mired_rgb[:, RGB_BLUE])
    def f_bd(x):
      mired_rgb = mired_to_rgb(x)
      return gamma_encode(mired_rgb[:, i] / mired_rgb[:, RGB_RED])
    y = numpy.concatenate([f_ab(x_ab), f_bd(x_bd)], 0)
    matplotlib.pyplot.plot(x, y)

  # red fit
  x_ab = numpy.linspace(a, b_red, 1000, numpy.double)
  x_bd = numpy.linspace(b_red, d, 1000, numpy.double)
  x = numpy.concatenate([x_ab, x_bd], 0)
  y = numpy.concatenate(
    [poly.eval(p_red_ab, x_ab), poly.eval(p_red_bd, x_bd)],
    0
  )
  matplotlib.pyplot.plot(x, y)

  # green fit
  x_ab = numpy.linspace(a, b_green, 1000, numpy.double)
  x_bd = numpy.linspace(b_green, d, 1000, numpy.double)
  x = numpy.concatenate([x_ab, x_bd], 0)
  y = numpy.concatenate(
    [poly.eval(p_green_ab, x_ab), poly.eval(p_green_bd, x_bd)],
    0
  )
  matplotlib.pyplot.plot(x, y)

  # blue fit
  x_ab = numpy.linspace(a, b_blue, 1000, numpy.double)
  x_bc = numpy.linspace(b_blue, c_blue, 1000, numpy.double)
  x_cd = numpy.linspace(c_blue, d, 1000, numpy.double)
  x = numpy.concatenate([x_ab, x_bc, x_cd], 0)
  y = numpy.concatenate(
    [
      poly.eval(p_blue_ab, x_ab),
      poly.eval(p_blue_bc, x_bc),
      poly.eval(p_blue_cd, x_cd)
    ],
    0
  )
  matplotlib.pyplot.plot(x, y)

  matplotlib.pyplot.show()

mired_to_rgb_fit = {
  'a': a,
  'b_red': float(b_red),
  'b_green': float(b_green),
  'b_blue': float(b_blue),
  'c_blue': float(c_blue),
  'd': d,
  'p_red_ab': p_red_ab,
  'p_red_ab_err': float(p_red_ab_err),
  'p_red_bd': p_red_bd,
  'p_red_bd_err': float(p_red_bd_err),
  'p_green_ab': p_green_ab,
  'p_green_ab_err': float(p_green_ab_err),
  'p_green_bd': p_green_bd,
  'p_green_bd_err': float(p_green_bd_err),
  'p_blue_ab': p_blue_ab,
  'p_blue_ab_err': float(p_blue_ab_err),
  'p_blue_bc': p_blue_bc,
  'p_blue_bc_err': float(p_blue_bc_err),
  'p_blue_cd': p_blue_cd,
  'p_blue_cd_err': float(p_blue_cd_err)
}
with open(mired_to_rgb_fit_out, 'w') as fout:
  yaml.dump(numpy_to_python(mired_to_rgb_fit), fout)
