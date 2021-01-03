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
import sys
from mired_to_rgb_display_p3 import mired_to_rgb_display_p3
from mired_to_rgb_rec2020 import mired_to_rgb_rec2020
from mired_to_rgb_srgb import mired_to_rgb_srgb

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

RGB_RED = 0
RGB_GREEN = 1
RGB_BLUE = 2
N_RGB = 3

# precompute RGB for 6504K, used for rgb_to_hsbk with kelv == None
# most generator scripts live in ../prepare, but this one is special,
# as it needs to run the previously generated code in this directory

if len(sys.argv) < 2:
  print(f'usage: {sys.argv[0]:s} device')
  print('device in {{srgb, display_p3, rec2020}}')
  sys.exit(EXIT_FAILURE)
device = sys.argv[1]

rgb = {
  'srgb': mired_to_rgb_srgb,
  'display_p3': mired_to_rgb_display_p3,
  'rec2020': mired_to_rgb_rec2020
}[device].convert(1e6 / 6504.)

print(
  f'''#!/usr/bin/env python3
# generated by rgb_to_hsbk_gen.py

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
from mired_to_rgb_{device:s} import mired_to_rgb_{device:s}
from rgb_to_hsbk import RGBToHSBK

rgb_to_hsbk_{device:s} = RGBToHSBK(
  numpy.array(
    [{rgb[RGB_RED]:.16e}, {rgb[RGB_GREEN]:.16e}, {rgb[RGB_BLUE]:.16e}],
    numpy.double
  ),
  mired_to_rgb_{device:s}
)

# standalone
if __name__ == '__main__':
  import rgb_to_hsbk

  rgb_to_hsbk.standalone(rgb_to_hsbk_{device:s})'''
)
