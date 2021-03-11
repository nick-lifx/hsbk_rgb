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
import protocol
import random
import sdl2
import time
from gamma_decode_rec2020 import gamma_decode_rec2020
from gamma_decode_srgb import gamma_decode_srgb
from gamma_encode_rec2020 import gamma_encode_rec2020
from gamma_encode_srgb import gamma_encode_srgb
from hsbk_to_rgb_display_p3 import hsbk_to_rgb_display_p3
from hsbk_to_rgb_rec2020 import hsbk_to_rgb_rec2020
from hsbk_to_rgb_srgb import hsbk_to_rgb_srgb
from hue_wheel import HueWheel
from udp import UDP

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

SET_COLOR_TIMEOUT = .1

device = 'srgb'
mac = None
hsbk = None
if len(sys.argv) >= 3 and sys.argv[1] == '--device':
  device = sys.argv[2]
  del sys.argv[1:3]
if len(sys.argv) >= 3 and sys.argv[1] == '--mac':
  mac = sys.argv[2]
  del sys.argv[1:3]
if len(sys.argv) >= 5:
  hsbk = numpy.array([float(i) for i in sys.argv[1:5]], numpy.double)

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

class Light:
  def __init__(self, mac, addr):
    self.mac = mac
    self.addr = addr
    self.sequence = random.randint(0, 0xff)
    self.timeout = None # if not None, send out_data when time reaches this
    self.out_data = None # if not None, indicates light is dirty and how to set

udp = UDP()
lights = {
  mac: Light(mac, addr)
  for mac, (addr, services) in udp.get_service(mac).items() # mac may be None
  if protocol.DeviceService.UDP in services
}

if hsbk is None:
  if len(lights):
    light = list(lights.values())[0]
    hsbk = udp.get_color(light.mac, light.addr)
  else:
    hsbk = numpy.array([0., 0., 1., 3500], numpy.double)

assert sdl2.SDL_Init(sdl2.SDL_INIT_TIMER | sdl2.SDL_INIT_VIDEO) == 0

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

# takes image as a numpy array of float, shape is (y_size, x_size, N_RGBA)
# returns surface, data; user must keep data alive for lifetime of surface
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
sdl2.SDL_FreeSurface(wheel_surface)
del wheel_data

event = sdl2.SDL_Event()
while True:
  sdl2.SDL_SetRenderTarget(renderer, None)
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
  sdl2.SDL_FreeSurface(dot_surface)
  del dot_data
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

  sdl2.SDL_RenderPresent(renderer)

  while True:
    # timer service in between events or upon timeout waiting for event
    try:
      in_data, in_addr = udp.socket.recvfrom(0x1000)
      frame = protocol.Frame()
      frame.deserialize(in_data)
      mac = frame.frame_address.target[:6].hex()
      light = lights.get(mac)
      if (
        light is not None and
          in_addr == light.addr and
          frame.frame_header.protocol == 1024 and
          frame.frame_header.addressable and
          frame.frame_header.source == udp.source and
          frame.frame_address.sequence == light.sequence and
          frame.protocol_header.type ==
            protocol.PacketType.DEVICE_ACKNOWLEDGEMENT
      ):
        light.timeout = None
        light.out_data = None
    except BlockingIOError:
      pass

    now = time.monotonic()
    for light in lights.values():
      if light.timeout is not None and now >= light.timeout:
        light.timeout += SET_COLOR_TIMEOUT
        udp.socket.sendto(light.out_data, light.addr)

    event.type = -1
    sdl2.SDL_WaitEventTimeout(ctypes.byref(event), 1)
    if event.type == sdl2.SDL_QUIT:
      sdl2.SDL_Quit()
      sys.exit(EXIT_SUCCESS)
    elif event.type == sdl2.SDL_MOUSEMOTION:
      if event.motion.state & sdl2.SDL_BUTTON_LMASK:
        hs, dist = hue_wheel.xy_to_hs(
          numpy.array(
            [event.motion.x - 12, event.motion.y - 120],
            numpy.double
          )
        )
        if dist < 60.:
          hsbk[:HSBK_BR] = hs
          now = time.monotonic()
          for light in lights.values():
            target = (bytes.fromhex(light.mac) + bytes(8))[:8]
            light.sequence = (light.sequence + 1) & 0xff
            light.out_data = protocol.Frame(
              frame_header = protocol.FrameHeader(
                source = udp.source
              ),
              frame_address = protocol.FrameAddress(
                target = target,
                ack_required = True,
                sequence = light.sequence
              ),
              protocol_header = protocol.ProtocolHeader(
                _type = protocol.PacketType.LIGHT_SET_COLOR
              ),
              payload = protocol.LightSetColor(
                color = protocol.LightHsbk(
                  hue = int(round((hsbk[HSBK_HUE] % 360.) * (0xffff / 360.))),
                  saturation = int(round(hsbk[HSBK_SAT] * 0xffff)),
                  brightness = int(round(hsbk[HSBK_BR] * 0xffff)),
                  kelvin = int(round(hsbk[HSBK_KELV]))
                )
              )
            ).serialize()
            if True: #light.timeout is None:
              light.timeout = now
          break
