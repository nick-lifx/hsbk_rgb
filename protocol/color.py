#!/usr/bin/env python3

# Copyright (c) 2021 Nick Downing
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

# put python into path
# temporary until we have proper Python packaging
import os.path
import sys
dirname = os.path.dirname(__file__)
sys.path.append(os.path.join(dirname, '../python'))

import numpy
import ctypes
import sdl2
import sdl2.sdlimage
#import sdl2.sdlttf
import udp
from gamma_decode_rec2020 import gamma_decode_rec2020
from gamma_decode_srgb import gamma_decode_srgb
from gamma_encode_rec2020 import gamma_encode_rec2020
from gamma_encode_srgb import gamma_encode_srgb
from hsbk_to_rgb_display_p3 import hsbk_to_rgb_display_p3
from hsbk_to_rgb_rec2020 import hsbk_to_rgb_rec2020
from hsbk_to_rgb_srgb import hsbk_to_rgb_srgb
from hue_wheel import HueWheel

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

HSBK_HUE = 0
HSBK_SAT = 1
HSBK_BR = 2
HSBK_KELV = 3
N_HSBK = 4

RGBA_RED = 0
RGBA_GREEN = 1
RGBA_BLUE = 2
RGBA_ALPHA = 3
N_RGBA = 4

XY_x = 0
XY_y = 1
N_XY = 2

device = 'srgb'
if len(sys.argv) >= 3 and sys.argv[1] == '--device':
  device = sys.argv[2]
  del sys.argv[1:3]
if len(sys.argv) < 5:
  print(f'usage: {sys.argv[0]:s} [--device device] hue sat br kelv')
  print('device in {display_p3, rec2020, srgb}, default srgb')
  print('hue = hue in degrees (0 to 360)')
  print('sat = saturation as fraction (0 to 1)')
  print('br = brightness as fraction (0 to 1)')
  print('kelv = white point in degrees Kelvin')
  sys.exit(EXIT_FAILURE)
hsbk = numpy.array(
  [
    float(sys.argv[1]),
    float(sys.argv[2]),
    float(sys.argv[3]),
    float(sys.argv[4])
  ],
  numpy.double
)

gamma_decode, gamma_encode, hsbk_to_rgb = {
  'display_p3': (
    gamma_decode_srgb,
    gamma_encode_srgb,
    hsbk_to_rgb_display_p3
  ),
  'rec2020': (
    gamma_decode_rec2020,
    gamma_encode_rec2020,
    hsbk_to_rgb_rec2020
  ),
  'srgb': (
    gamma_decode_srgb,
    gamma_encode_srgb,
    hsbk_to_rgb_srgb
  )
}[device]

hue_wheel = HueWheel(gamma_decode, gamma_encode, hsbk_to_rgb, 120, 15)

assert sdl2.SDL_Init(sdl2.SDL_INIT_TIMER | sdl2.SDL_INIT_VIDEO) == 0
assert sdl2.sdlimage.IMG_Init(sdl2.sdlimage.IMG_INIT_PNG) #== 0
#assert sdl2.sdlttf.TTF_Init() == 0

window = sdl2.SDL_CreateWindow(
  b'Color',
  sdl2.SDL_WINDOWPOS_UNDEFINED,
  sdl2.SDL_WINDOWPOS_UNDEFINED,
  272,
  480,
  sdl2.SDL_WINDOW_HIDDEN
)
sdl2.SDL_ShowWindow(window)

renderer = sdl2.SDL_CreateRenderer(window, -1, sdl2.SDL_RENDERER_ACCELERATED)
#font = sdl2.sdlttf.TTF_OpenFont(
#  b'/usr/share/fonts/truetype/msttcorefonts/Arial.ttf',
#  14
#)

# takes image as a numpy array of float, shape is (y_size, x_size, N_RGBA)
# returns surface, data, user must keep data alive for lifetime of surface
def image_to_surface(image):
  y_size, x_size, channels = image.shape
  assert channels == N_RGBA

  data = numpy.round(image * 255.).astype(numpy.uint8).tobytes()
  return sdl2.SDL_CreateRGBSurfaceFrom(
    data,
    x_size, # width
    y_size, # height
    32, # depth
    x_size * 4, # pitch
    0x000000ff, # rmask
    0x0000ff00, # gmask
    0x00ff0000, # gmask
    0xff000000, # amask
  ), data

wheel_surface, wheel_data = image_to_surface(
  hue_wheel.render_wheel(hsbk[HSBK_BR:])
)
wheel_texture = sdl2.SDL_CreateTextureFromSurface(renderer, wheel_surface)

while True:
  sdl2.SDL_SetRenderTarget(renderer, None)
  #sdl2.SDL_SetRenderDrawColor(renderer, 0, 0, 0, 0xff)
  sdl2.SDL_RenderClear(renderer)

  sdl2.SDL_RenderCopy(renderer,
    wheel_texture,
    None,
    sdl2.SDL_Rect(16, 120, 241, 241)
  )

  xy = hue_wheel.hs_to_xy(hsbk[:HSBK_BR])
  xy_frac, xy_int = numpy.modf(xy)
  dot_surface, dot_data = image_to_surface(
    hue_wheel.render_dot(hsbk, xy_frac[XY_x], xy_frac[XY_y])
  )
  dot_texture = sdl2.SDL_CreateTextureFromSurface(renderer, dot_surface)
  sdl2.SDL_RenderCopy(renderer,
    dot_texture,
    None,
    sdl2.SDL_Rect(
      16 - 15 + int(xy_int[XY_x]),
      120 - 15 + int(xy_int[XY_y]),
      31,
      31
    )
  )
  sdl2.SDL_DestroyTexture(dot_texture)
  sdl2.SDL_FreeSurface(dot_surface)
  del dot_data

  sdl2.SDL_RenderPresent(renderer)

  event = sdl2.SDL_Event()
  while True:
    sdl2.SDL_WaitEvent(ctypes.byref(event))
    if event.type == sdl2.SDL_QUIT:
      #sdl2.sdlttf.TTF_Quit()
      sdl2.sdlimage.IMG_Quit()
      sdl2.SDL_Quit()
      sys.exit(EXIT_SUCCESS)

    if event.type == sdl2.SDL_MOUSEMOTION:
      if event.motion.state & sdl2.SDL_BUTTON_LMASK:
        hs, within = hue_wheel.xy_to_hs(
          numpy.array(
            [event.motion.x - 12, event.motion.y - 120],
            numpy.double
          )
        )
        if True: #within:
          hsbk[:HSBK_BR] = hs
          break
