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
from hsbk_to_rgb import hsbk_to_rgb

RGB_RED = 0
RGB_GREEN = 1
RGB_BLUE = 2
N_RGB = 3

# precompute RGB for 6504K, used for rgb_to_hsbk with kelv == None

rgb = hsbk_to_rgb(numpy.array([0., 0., 1., 6504.], numpy.double))
print(
  '''import numpy

kelv_rgb_6504K = numpy.array(
  [{0:.16e}, {1:.16e}, {2:.16e}],
  numpy.double
)'''.format(rgb[RGB_RED], rgb[RGB_GREEN], rgb[RGB_BLUE])
)
