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

import numpy
import utils.yaml_io

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

#numpy.set_printoptions(threshold = numpy.inf)

if len(sys.argv) < 2:
  print(f'usage: {sys.argv[0]:s} xy_to_r_fit_in.yml')
  sys.exit(EXIT_FAILURE)
xy_to_r_fit_in = sys.argv[1]

xy_to_r_fit = utils.yaml_io._import(
  utils.yaml_io.read_file(xy_to_r_fit_in)
)
p = xy_to_r_fit['p']
err = xy_to_r_fit['err']

sys.stdout.write(
  sys.stdin.read().format(
    max_err = numpy.max(err),
    p00 = p[0, 0],
    p01 = p[0, 1],
    p10 = p[1, 0],
    p11 = p[1, 1],
    p20 = p[2, 0],
    p21 = p[2, 1]
  )
)
