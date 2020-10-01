#!/usr/bin/env python3

import numpy
import numpy.linalg
import math
import matplotlib.pyplot
import poly
import ruamel.yaml
import sys
from numpy_to_python import numpy_to_python
from python_to_numpy import python_to_numpy

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
D65_XYZ = numpy.array([.3127, .3290, 1. - .3127 - .3290], numpy.double)
def srgb_gamma_encode(x):
  return x * 12.92 if x < .0031308 else 1.055 * x ** (1. / 2.4) - .055

# approximation order can be set separately for each channel and interval
ORDER_RED_AB = 4
ORDER_GREEN_AB = 4
ORDER_GREEN_BD = 6
ORDER_BLUE_BC = 8

EPSILON = 1e-12

diag = False
if len(sys.argv) >= 2 and sys.argv[1] == '--diag':
  diag = True
  del sys.argv[1]
if len(sys.argv) < 4:
  print(f'usage: {sys.argv[0]:s} [--diag] mired_to_uv_data_in.yml rgb(w)_to_(xy|XYZ)_in.yml mired_to_rgb_fit_out.yml')
  sys.exit(EXIT_FAILURE)
mired_to_uv_data_in = sys.argv[1]
rgbw_to_XYZ_in = sys.argv[2]
mired_to_rgb_fit_out = sys.argv[3]

yaml = ruamel.yaml.YAML(typ = 'safe')
#numpy.set_printoptions(threshold = numpy.inf)

with open(mired_to_uv_data_in) as fin:
  mired_to_uv_data = python_to_numpy(yaml.load(fin))
mired_scale = mired_to_uv_data['mired_scale']
data_points = mired_to_uv_data['data_points']
n_mired, _ = data_points.shape

with open(rgbw_to_XYZ_in) as fin:
  rgbw_to_XYZ = python_to_numpy(yaml.load(fin))
if rgbw_to_XYZ.shape[0] < N_XYZ:
  # it is only chromaticities, add the missing z coordinate
  x = rgbw_to_XYZ[XY_x, :]
  y = rgbw_to_XYZ[XY_y, :]
  rgbw_to_XYZ = numpy.stack([x, y, 1. - x - y], 0)

# ignore white LED/point, fudge intensities to give it a D65 white point
intensity_fudge = numpy.linalg.solve(rgbw_to_XYZ[:, :RGBW_WHITE], D65_XYZ)
#print('intensity_fudge', intensity_fudge)
rgb_to_XYZ = rgbw_to_XYZ[:, :RGBW_WHITE] * intensity_fudge[numpy.newaxis, :]
#print('rgb_to_XYZ', rgb_to_XYZ)
rgb_to_UVW = XYZ_to_UVW @ rgb_to_XYZ
#print('rgb_to_UVW', rgb_to_UVW)
UVW_to_rgb = numpy.linalg.inv(rgb_to_UVW)
#print('UVW_to_rgb', UVW_to_rgb)

# convert mired scale to around 1 and data points uv -> UVW -> rgb
u = data_points[:, 0]
v = data_points[:, 1]
UVW = numpy.stack([u, v, 1. - u - v], 1)
mired_rgb = numpy.einsum('ij,kj->ki', UVW_to_rgb, UVW)
#print('mired_rgb', mired_rgb)

#if diag:
#  matplotlib.pyplot.plot(x, mired_rgb[:, RGB_RED])
#  matplotlib.pyplot.plot(x, mired_rgb[:, RGB_GREEN])
#  matplotlib.pyplot.plot(x, mired_rgb[:, RGB_BLUE])
#  matplotlib.pyplot.show()

# mired scale must meet the following specification:
#   a <= x <= b: blue is at 1, red and green are increasing
#   b <= x <= c: red is at 1, blue and green are decreasing
#   c <= x <= d: red is at 1, blue is at 0, green is decreasing
# where [a, d] is the domain, e.g. [1e6 / 15000, 1e6 / 1000]
# in the next part we approximate b and c by scanning the array to
# find coarse intersection and then refining by linear interpolation
mired_a_index = 0.
print('mired_a_index', mired_a_index)
for i in range(n_mired - 2):
  y0 = mired_rgb[i, RGB_BLUE] - mired_rgb[i, RGB_RED]
  y1 = mired_rgb[i + 1, RGB_BLUE] - mired_rgb[i + 1, RGB_RED]
  if y0 >= 0. and y1 < 0.:
    # y0 + x (y1 - y0) = 0
    m = y1 - y0
    j = -y0 / m if abs(m) >= EPSILON else .5
    mired_b_index = i + j
    break
else:
  assert False
print('mired_b_index', mired_b_index)
for i in range(n_mired - 2):
  y0 = mired_rgb[i, RGB_BLUE]
  y1 = mired_rgb[i + 1, RGB_BLUE]
  if y0 >= 0. and y1 < 0.:
    # y0 + x (y1 - y0) = 0
    m = y1 - y0
    j = -y0 / m if abs(m) >= EPSILON else .5
    mired_c_index = i + j
    break
else:
  assert False
print('mired_c_index', mired_c_index)
mired_d_index = n_mired - 1.
print('mired_d_index', mired_d_index)

# in what follows y0(x) is taken to be the ideal function from the
# given data, whereas y1(x) is a polynomial approximation -- in the
# first case user provides information about channels and mired_rgb
# array is implicit, in the second case user provides a polynomial

# takes pseudo coordinate x, it is an index into mired_scale + a fraction
# let f_channel(x) denote the intensity for a given channel and mireds
# returns y(x) = srgb_gamma_encode(f_channel(x) / f_limiting_channel(x))
def eval_y0(channel, limiting_channel, x_index):
  i = int(math.floor(x_index))
  if i < 0:
    i = 0
  if i > n_mired - 2:
    i = n_mired - 2
  j = x_index - i
  y0 = mired_rgb[i, channel]
  y1 = mired_rgb[i + 1, channel]
  y_channel = y0 + j * (y1 - y0)
  y0 = mired_rgb[i, limiting_channel]
  y1 = mired_rgb[i + 1, limiting_channel]
  y_limiting_channel = y0 + j * (y1 - y0)
  return srgb_gamma_encode(y_channel / y_limiting_channel)

# takes pseudo coordinate, it is an index into mired_scale + a fraction
# returns actual coordinate, in mireds * (1 << MIRED_SCALE_BITS) / 1e6
def eval_x(x_index):
  i = int(math.floor(x_index))
  if i < 0:
    i = 0
  if i > n_mired - 2:
    i = n_mired - 2
  j = x_index - i
  x0 = mired_scale[i]
  x1 = mired_scale[i + 1]
  return x0 + j * (x1 - x0)

# takes pseudo coordinate, converts and evaluates the given polynomial
def eval_y1(p, x_index):
  return poly.eval(p, eval_x(x_index))

# generic function that can perform Remez algorithm on a given
# channel and interval, returning a polynomial of a given order
def remez(channel, limiting_channel, a, b, order):
  j0 = int(math.floor(a + EPSILON))
  j1 = int(math.ceil(b - EPSILON)) + 1

  # put minimax nodes halfway between chebyshev nodes on unit circle initially
  x_index = a + (b - a) * (
    .5 + .5 * numpy.cos(
      numpy.arange(order, -1, -1, numpy.int32) * math.pi / order
    )
  )
  print('x_index', x_index)
  for i in range(10):
    print('i', i)

    # find approximation of given order by fitting to minimax nodes with osc
    x = numpy.array(
      [eval_x(x_index[i]) for i in range(order + 1)],
      numpy.double
    )
    #print('x', x)
    A = numpy.concatenate(
      [
        x[:, numpy.newaxis] ** numpy.arange(order, dtype = numpy.int32),
        (
          (-1.) ** numpy.arange(order + 1, dtype = numpy.int32)
        )[:, numpy.newaxis]
      ],
      1
    )
    y = numpy.array(
      [
        eval_y0(channel, limiting_channel, x_index[i])
        for i in range(order + 1)
      ],
      numpy.double
    )
    #print('y', y)
    col_scale = numpy.min(numpy.abs(A), 0) ** -.5
    row_scale = numpy.min(numpy.abs(A), 1) ** -.5
    p = numpy.linalg.solve(
      A * (col_scale[numpy.newaxis, :] * row_scale[:, numpy.newaxis]),
      y * row_scale
    ) * col_scale
    osc = p[-1]
    print('osc', osc)
    p = p[:-1]
    #print('p', p)

    # checking
    #err = numpy.array(
    #  [
    #    eval_y1(p, x_index[i]) -
    #      eval_y0(channel, limiting_channel, x_index[i])
    #    for i in range(order + 1)
    #  ],
    #  numpy.double
    #)
    #print('err', err)

    # compute error function coarsely and then scan for zero crossings
    # (isolates maxima/minima by partitioning into positive and negative)
    # refine x coordinate of each zero-crossing by linear interpolation
    #x = [eval_x(j) for j in range(j0, j1)]
    #print('x', x)
    err = numpy.array(
      [
        eval_y1(p, j) - eval_y0(channel, limiting_channel, j)
        for j in range(j0, j1)
      ],
      numpy.double
    )
    #print('err', err)
    err_pos = err >= 0.
    #print('err_pos', err_pos)
    z = [a]
    z_pos = [err_pos[0]]
    for j in numpy.nonzero(err_pos[1:] != err_pos[:-1])[0]:
      e0 = err[j]
      e1 = err[j + 1]
      # e0 + x (e1 - e0) = 0
      m = e1 - e0
      k = -e0 / m if abs(m) >= EPSILON else .5
      x = j0 + j + k
      if x > a and x < b:
        z.append(x)
        z_pos.append(err_pos[j + 1])
    z.append(b)
    z = numpy.array(z, numpy.double)
    #print('z', z)
    z_pos = numpy.array(z_pos, numpy.bool)
    #print('z_pos', z_pos)
    n_intervals, = z_pos.shape
    if n_intervals < order + 1:
      print('warning: not enough intervals -- we say good enough')
      break

    # perform a bracketing search in each interval
    # suppose the interval [c, d] is known to contain a maximum y(x)
    # then find e, f such that c < e < f < d and calculate y(e), y(f)
    # if y(e) < y(f) then replace c with e otherwise replace d with f
    x_index = []
    for j in range(n_intervals):
      c = z[j]
      d = z[j + 1]
      #print('j', j, 'c', c, 'd', d)
      for k in range(20):
        e = c + 1. / 3. * (d - c)
        ee = eval_y1(p, e) - eval_y0(channel, limiting_channel, e)
        f = c + 2. / 3. * (d - c)
        ef = eval_y1(p, f) - eval_y0(channel, limiting_channel, f)
        #print('k', k, 'e', e, 'err(e)', ee, 'f', f, 'err(f)', ef)
        if (ee < ef) == z_pos[j]:
          c = e
        else:
          d = f
      x_index.append(.5 * (c + d))
    x_index = numpy.array(x_index, numpy.double)
    #print('x_index', x_index)

    # drop minimax nodes from either end according to least error
    while x_index.shape[0] > order + 1:
      err0 = (
        eval_y1(p, x_index[0]) -
          eval_y0(channel, limiting_channel, x_index[0])
      )
      err1 = (
        eval_y1(p, x_index[-1]) -
          eval_y0(channel, limiting_channel, x_index[-1])
      )
      print('drop', err0, err1)
      x_index = x_index[1:] if abs(err0) < abs(err1) else x_index[:1]
    print('x_index', x_index)

    # checking
    #x = numpy.array(
    #  [eval_x(x_index[i]) for i in range(order + 1)],
    #  numpy.double
    #)
    #print('x', x)
    err = numpy.array(
      [
        eval_y1(p, x_index[i]) -
          eval_y0(channel, limiting_channel, x_index[i])
        for i in range(order + 1)
      ],
      numpy.double
    )
    print('err', err)
  return p

# red channel
p_red_ab = remez(
  RGB_RED,
  RGB_BLUE,
  mired_a_index,
  mired_b_index,
  ORDER_RED_AB
)
print('p_red_ab', p_red_ab)
p_red_bd = numpy.array([1.], numpy.double)
print('p_red_bd', p_red_bd)

# green channel
p_green_ab = remez(
  RGB_GREEN,
  RGB_BLUE,
  mired_a_index,
  mired_b_index,
  ORDER_GREEN_AB
)
print('p_green_ab', p_green_ab)
p_green_bd = remez(
  RGB_GREEN,
  RGB_RED,
  mired_b_index,
  mired_d_index,
  ORDER_GREEN_BD
)
print('p_green_bd', p_green_bd)

# blue channel
p_blue_ab = numpy.array([1.], numpy.double)
print('p_blue_ab', p_blue_ab)
p_blue_bc = remez(
  RGB_BLUE,
  RGB_RED,
  mired_b_index,
  mired_c_index,
  ORDER_BLUE_BC
)
print('p_blue_bc', p_blue_bc)
p_blue_cd = numpy.array([0.], numpy.double)
print('p_blue_cd', p_blue_cd)

# fix discontinuities by setting mired_b, mired_c to exact intersection
# of the fitted polynomials (need a different mired_b_index for each channel)
def newton(p, x):
  p_deriv = poly.deriv(p)
  for i in range(5):
    x -= poly.eval(p, x) / poly.eval(p_deriv, x)
    #print('i', i, 'x', x, 'p(x)', poly.eval(p, x))
  return x
mired_a = eval_x(mired_a_index)
mired_b = eval_x(mired_b_index)
mired_c = eval_x(mired_c_index)
mired_d = eval_x(mired_d_index)
mired_b_red = newton(poly.add(p_red_ab, -p_red_bd), mired_b)
mired_b_green = newton(poly.add(p_green_ab, -p_green_bd), mired_b)
mired_b_blue = newton(poly.add(p_blue_ab, -p_blue_bc), mired_b)
mired_c = newton(poly.add(p_blue_bc, -p_blue_cd), mired_c)

if diag:
  # ideal
  x_ab = numpy.linspace(mired_a_index, mired_b_index, 1000, numpy.double)
  x_bd = numpy.linspace(mired_b_index, mired_d_index, 1000, numpy.double)
  x = numpy.array(
    [eval_x(x_ab[i]) for i in range(x_ab.shape[0])] +
      [eval_x(x_bd[i]) for i in range(x_bd.shape[0])],
    numpy.double
  )
  for i in range(N_RGB):
    y = numpy.array(
      [eval_y0(i, RGB_BLUE, x_ab[j]) for j in range(x_ab.shape[0])] +
        [eval_y0(i, RGB_RED, x_bd[j]) for j in range(x_bd.shape[0])],
      numpy.double
    )
    matplotlib.pyplot.plot(x, y)

  # red fit
  x_ab = numpy.linspace(mired_a, mired_b_red, 1000, numpy.double)
  x_bd = numpy.linspace(mired_b_red, mired_d, 1000, numpy.double)
  x = numpy.concatenate([x_ab, x_bd], 0)
  y = numpy.concatenate(
    [poly.eval(p_red_ab, x_ab), poly.eval(p_red_bd, x_bd)],
    0
  )
  matplotlib.pyplot.plot(x, y)

  # green fit
  x_ab = numpy.linspace(mired_a, mired_b_green, 1000, numpy.double)
  x_bd = numpy.linspace(mired_b_green, mired_d, 1000, numpy.double)
  x = numpy.concatenate([x_ab, x_bd], 0)
  y = numpy.concatenate(
    [poly.eval(p_green_ab, x_ab), poly.eval(p_green_bd, x_bd)],
    0
  )
  matplotlib.pyplot.plot(x, y)

  # blue fit
  x_ab = numpy.linspace(mired_a, mired_b_blue, 1000, numpy.double)
  x_bc = numpy.linspace(mired_b_blue, mired_c, 1000, numpy.double)
  x_cd = numpy.linspace(mired_c, mired_d, 1000, numpy.double)
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
  'red_boost': float(intensity_fudge[RGB_GREEN] / intensity_fudge[RGB_RED]),
  'blue_boost': float(intensity_fudge[RGB_GREEN] / intensity_fudge[RGB_BLUE]),
  'mired_a': float(mired_a),
  'mired_b_red': float(mired_b_red),
  'mired_b_green': float(mired_b_green),
  'mired_b_blue': float(mired_b_blue),
  'mired_c': float(mired_c),
  'mired_d': float(mired_d),
  'p_red_ab': p_red_ab,
  'p_red_bd': p_red_bd,
  'p_green_ab': p_green_ab,
  'p_green_bd': p_green_bd,
  'p_blue_ab': p_blue_ab,
  'p_blue_bc': p_blue_bc,
  'p_blue_cd': p_blue_cd
}
with open(mired_to_rgb_fit_out, 'w') as fout:
  yaml.dump(numpy_to_python(mired_to_rgb_fit), fout)
