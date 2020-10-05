#!/usr/bin/env python3

import numpy
import numpy.linalg
import math
import poly
import ruamel.yaml
import sys
from any_f_to_poly import any_f_to_poly
from blackbody_spectrum import blackbody_spectra
from numpy_to_python import numpy_to_python
from python_to_numpy import python_to_numpy
from remez import remez

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

RGB_RED = 0
RGB_GREEN = 1
RGB_BLUE = 2
N_RGB = 3

RGBW_RED = 0
RGBW_GREEN = 1
RGBW_BLUE = 2
RGBW_WHITE = 3
N_RGBW = 4

XY_x = 0
XY_y = 1
N_XY = 2

XYZ_X = 0
XYZ_Y = 1
XYZ_Z = 2
N_XYZ = 3

# see https://en.wikipedia.org/wiki/CIE_1960_color_space
XYZ_to_UVW = numpy.array(
  [
    [2. / 3., 0., 0.],
    [0., 1., 0.],
    [-1. / 2., 3. / 2, 1. / 2.]
  ],
  numpy.double
)

# see https://en.wikipedia.org/wiki/SRGB
def gamma_encode(x):
  x = numpy.copy(x)
  mask = x < .0031308
  x[mask] *= 12.92
  x[~mask] = x[~mask] ** (1. / 2.4) * 1.055 - .055
  return x

ORDER0 = 18

# approximation order can be set separately for each channel and interval
ORDER_RED_AB = 4
ORDER_GREEN_AB = 4
ORDER_GREEN_BD = 6
ORDER_BLUE_BC = 8

EPSILON = 1e-48

diag = False
if len(sys.argv) >= 2 and sys.argv[1] == '--diag':
  diag = True
  del sys.argv[1]
if len(sys.argv) < 5:
  print(f'usage: {sys.argv[0]:s} primaries_in.yml b_estimate c_estimate mired_to_rgb_fit_out.yml')
  sys.exit(EXIT_FAILURE)
primaries_in = sys.argv[1]
b_estimate = float(sys.argv[2])
c_estimate = float(sys.argv[3])
mired_to_rgb_fit_out = sys.argv[4]

yaml = ruamel.yaml.YAML(typ = 'safe')
#numpy.set_printoptions(threshold = numpy.inf)

with open('standard_observer_2deg.yml') as fin:
  standard_observer_2deg = python_to_numpy(yaml.load(fin))

with open(primaries_in) as fin:
  primaries = python_to_numpy(yaml.load(fin))
XYZ_to_rgb = primaries['XYZ_to_rgb']

# functions to be approximated
def mired_to_XYZ(x):
  return numpy.einsum(
    'ij,ik->kj',
    blackbody_spectra(1e6 / x),
    standard_observer_2deg
  )

# to use:
# def f_r(x):
#   return XYZ_to_rgb[RGB_RED, :] @ mired_to_XYZ(x)
# def f_g(x):
#   return XYZ_to_rgb[RGB_GREEN, :] @ mired_to_XYZ(x)
# def f_b(x):
#   return XYZ_to_rgb[RGB_BLUE, :] @ mired_to_XYZ(x)

# mired scale must meet the following specification:
#   a <= x <= b: blue is at 1, red and green are increasing
#   b <= x <= c: red is at 1, blue and green are decreasing
#   c <= x <= d: red is at 1, blue is at 0, green is decreasing
# where [a, d] is the domain, e.g. [1e6 / 15000, 1e6 / 1000]

a = 1e6 / 15000.
print('a', a)
d = 1e6 / 1000.
print('d', d)

# find b, i.e. where red meets blue
def f(x):
  return (XYZ_to_rgb[RGB_RED, :] - XYZ_to_rgb[RGB_BLUE, :]) @ mired_to_XYZ(x)
b = poly.newton(
  any_f_to_poly(f, b_estimate - 100., b_estimate + 100., ORDER0),
  b_estimate
)
print('b', b)

# find c, i.e. where blue meets 0
def f(x):
  return XYZ_to_rgb[RGB_BLUE, :] @ mired_to_XYZ(x)
c = poly.newton(
  any_f_to_poly(f, c_estimate - 100., c_estimate + 100., ORDER0),
  c_estimate
)
print('c', c)

# red channel
def f(x):
  XYZ = mired_to_XYZ(x)
  return gamma_encode(
    (XYZ_to_rgb[RGB_RED, :] @ XYZ) / (XYZ_to_rgb[RGB_BLUE, :] @ XYZ)
  )
p_red_ab, p_red_ab_err = remez(
  any_f_to_poly(f, a, b, ORDER0),
  a,
  b,
  ORDER_RED_AB,
  epsilon = EPSILON
)
print('p_red_ab', p_red_ab)
print('p_red_ab_err', p_red_ab_err)
p_red_bd = numpy.array([1.], numpy.double)
p_red_bd_err = 0.

# green channel
def f(x):
  XYZ = mired_to_XYZ(x)
  return gamma_encode(
    (XYZ_to_rgb[RGB_GREEN, :] @ XYZ) / (XYZ_to_rgb[RGB_BLUE, :] @ XYZ)
  )
p_green_ab, p_green_ab_err = remez(
  any_f_to_poly(f, a, b, ORDER0),
  a,
  b,
  ORDER_GREEN_AB,
  epsilon = EPSILON
)
print('p_green_ab', p_green_ab)
print('p_green_ab_err', p_green_ab_err)
def f(x):
  XYZ = mired_to_XYZ(x)
  return gamma_encode(
    (XYZ_to_rgb[RGB_GREEN, :] @ XYZ) / (XYZ_to_rgb[RGB_RED, :] @ XYZ)
  )
p_green_bd, p_green_bd_err = remez(
  any_f_to_poly(f, b, d, ORDER0),
  b,
  d,
  ORDER_GREEN_BD,
  epsilon = EPSILON
)
print('p_green_bd', p_green_bd)
print('p_green_bd_err', p_green_bd_err)

# blue channel
p_blue_ab = numpy.array([1.], numpy.double)
p_blue_ab_err = 0.
def f(x):
  XYZ = mired_to_XYZ(x)
  return gamma_encode(
    (XYZ_to_rgb[RGB_BLUE, :] @ XYZ) / (XYZ_to_rgb[RGB_RED, :] @ XYZ)
  )
p_blue_bc, p_blue_bc_err = remez(
  any_f_to_poly(f, b, c, ORDER0),
  b,
  c,
  ORDER_BLUE_BC,
  epsilon = EPSILON
)
print('p_blue_bc', p_blue_bc)
print('p_blue_bc_err', p_blue_bc_err)
p_blue_cd = numpy.array([0.], numpy.double)
p_blue_cd_err = 0.

# fix discontinuities by setting b, c to exact intersection after fitting
b_red = poly.newton(poly.add(p_red_ab, -p_red_bd), b)
print('b_red', b_red)
b_green = poly.newton(poly.add(p_green_ab, -p_green_bd), b)
print('b_green', b_green)
b_blue = poly.newton(poly.add(p_blue_ab, -p_blue_bc), b)
print('b_blue', b_blue)
c_blue = poly.newton(poly.add(p_blue_bc, -p_blue_cd), c)
print('c_blue', c_blue)

if diag:
  import matplotlib.pyplot

  # ideal
  x_ab = numpy.linspace(a, b, 1000, numpy.double)
  x_bd = numpy.linspace(b, d, 1000, numpy.double)
  x = numpy.concatenate([x_ab, x_bd], 0)
  for i in range(N_RGB):
    def f_ab(x):
      XYZ = mired_to_XYZ(x)
      #return XYZ_to_rgb[i, :] @ XYZ
      return gamma_encode(
        (XYZ_to_rgb[i, :] @ XYZ) / (XYZ_to_rgb[RGB_BLUE, :] @ XYZ)
      )
    def f_bd(x):
      XYZ = mired_to_XYZ(x)
      #return XYZ_to_rgb[i, :] @ XYZ
      return gamma_encode(
        (XYZ_to_rgb[i, :] @ XYZ) / (XYZ_to_rgb[RGB_RED, :] @ XYZ)
      )
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
