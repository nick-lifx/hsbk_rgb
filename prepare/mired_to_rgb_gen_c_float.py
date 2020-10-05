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

if len(sys.argv) < 2:
  print(f'usage: {sys.argv[0]:s} mired_to_rgb_fit_in.yml [name]')
  sys.exit(EXIT_FAILURE)
mired_to_rgb_fit_in = sys.argv[1]
name = sys.argv[2] if len(sys.argv) >= 3 else 'mired_to_rgb'

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
  '''// generated by ../prepare/mired_to_rgb_gen_c_float.py

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

#include <assert.h>
#include "mired_to_rgb.h"

#define RGB_RED 0
#define RGB_GREEN 1
#define RGB_BLUE 2
#define N_RGB 3

#define EPSILON 1e-6

void {0:s}(float mired, float *rgb) {{
  // validate inputs, allowing a little slack
  assert(mired >= {1:.8e}f * (1.f - EPSILON) && mired < {2:.8e}f * (1.f + EPSILON));

  // calculate red channel
  float r;
  if (mired < {3:.8e}f) {{
    r = {4:.8e}f;
{5:s}  }}
  else {{
    r = {6:.8e}f;
{7:s}  }}
  rgb[RGB_RED] = r;

  // calculate green channel
  float g;
  if (mired < {8:.8e}f) {{
    g = {9:.8e}f;
{10:s}  }}
  else {{
    g = {11:.8e}f;
{12:s}  }}
  rgb[RGB_GREEN] = g;

  // calculate blue channel
  float b;
  if (mired < {13:.8e}f) {{
    b = {14:.8e}f;
{15:s}  }}
  else if (mired < {16:.8e}f) {{
    b = {17:.8e}f;
{18:s}  }}
  else {{
    b = {19:.8e}f;
{20:s}  }}
  rgb[RGB_BLUE] = b;
}}

#ifdef STANDALONE
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv) {{
  if (argc < 2) {{
    printf(
      "usage: %s mired\\n"
        "mired = colour temperature in micro reciprocal degrees Kelvin\\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }}
  float mired = atof(argv[1]);

  float rgb[N_RGB];
  {21:s}(mired, rgb);
  printf(
    "mired %.3f -> RGB (%.6f, %.6f, %.6f)\\n",
    mired,
    rgb[RGB_RED],
    rgb[RGB_GREEN],
    rgb[RGB_BLUE]
  );

  return EXIT_SUCCESS;
}}
#endif'''.format(
    name,
    a,
    d,
    b_red,
    p_red_ab[-1],
    ''.join(
      [
        '    r = r * mired {0:s} {1:.8e}f;\n'.format(
          '+' if p_red_ab[i] >= 0 else '-',
          abs(p_red_ab[i])
        )
        for i in range(p_red_ab.shape[0] - 2, -1, -1)
      ]
    ),
    p_red_bd[-1],
    ''.join(
      [
        '    r = r * mired {0:s} {1:.8e}f;\n'.format(
          '+' if p_red_bd[i] >= 0 else '-',
          abs(p_red_bd[i])
        )
        for i in range(p_red_bd.shape[0] - 2, -1, -1)
      ]
    ),
    b_green,
    p_green_ab[-1],
    ''.join(
      [
        '    g = g * mired {0:s} {1:.8e}f;\n'.format(
          '+' if p_green_ab[i] >= 0 else '-',
          abs(p_green_ab[i])
        )
        for i in range(p_green_ab.shape[0] - 2, -1, -1)
      ]
    ),
    p_green_bd[-1],
    ''.join(
      [
        '    g = g * mired {0:s} {1:.8e}f;\n'.format(
          '+' if p_green_bd[i] >= 0 else '-',
          abs(p_green_bd[i])
        )
        for i in range(p_green_bd.shape[0] - 2, -1, -1)
      ]
    ),
    b_blue,
    p_blue_ab[-1],
    ''.join(
      [
        '    b = b * mired {0:s} {1:.8e}f;\n'.format(
          '+' if p_blue_ab[i] >= 0 else '-',
          abs(p_blue_ab[i])
        )
        for i in range(p_blue_ab.shape[0] - 2, -1, -1)
      ]
    ),
    c_blue,
    p_blue_bc[-1],
    ''.join(
      [
        '    b = b * mired {0:s} {1:.8e}f;\n'.format(
          '+' if p_blue_bc[i] >= 0 else '-',
          abs(p_blue_bc[i])
        )
        for i in range(p_blue_bc.shape[0] - 2, -1, -1)
      ]
    ),
    p_blue_cd[-1],
    ''.join(
      [
        '    b = b * mired {0:s} {1:.8e}f;\n'.format(
          '+' if p_blue_cd[i] >= 0 else '-',
          abs(p_blue_cd[i])
        )
        for i in range(p_blue_cd.shape[0] - 2, -1, -1)
      ]
    ),
    name
  )
)
