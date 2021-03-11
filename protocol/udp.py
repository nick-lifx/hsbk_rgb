#!/usr/bin/env python3

import protocol
import random
import select
import socket
import sys
import time

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

GET_SERVICE_TRIES = 5
GET_SERVICE_TIMEOUT = .1

GET_VERSION_TRIES = 5
GET_VERSION_TIMEOUT = .1

SET_COLOR_TRIES = 5
SET_COLOR_TIMEOUT = .1

HSBK_HUE = 0
HSBK_SAT = 1
HSBK_BR = 2
HSBK_KELV = 3
N_HSBK = 4

class UDPException(Exception):
  pass

class UDP:
  def __init__(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    self.socket.setblocking(0)
    self.socket.bind(('0.0.0.0', 0))

    self.source = random.randint(0, 0xffffffff)
    self.sequence = random.randint(0, 0xff)

  def get_service(self, mac = None):
    target = bytes(8) if mac is None else (bytes.fromhex(mac) + bytes(8))[:8]
    self.sequence = (self.sequence + 1) & 0xff
    out_data = protocol.Frame(
      frame_header = protocol.FrameHeader(
        source = self.source
      ),
      frame_address = protocol.FrameAddress(
        target = target,
        res_required = True,
        sequence = self.sequence
      ),
      protocol_header = protocol.ProtocolHeader(
        _type = protocol.PacketType.DEVICE_GET_SERVICE
      )
    ).serialize()

    now = time.monotonic()
    timeout = now
    result = {}
    for i in range(GET_SERVICE_TRIES):
      self.socket.sendto(out_data, ('255.255.255.255', 56700))

      timeout += GET_SERVICE_TIMEOUT
      while now < timeout:
        r, _, _ = select.select([self.socket], [], [], timeout - now)
        if len(r):
          in_data, in_addr = self.socket.recvfrom(0x1000)
          frame = protocol.Frame()
          frame.deserialize(in_data)
          if (
            frame.frame_header.protocol == 1024 and
              frame.frame_header.addressable and
              frame.frame_header.source == self.source and
              frame.frame_address.sequence == self.sequence and
              frame.protocol_header.type ==
                protocol.PacketType.DEVICE_STATE_SERVICE
          ):
            mac = frame.frame_address.target[:6].hex()
            if mac not in result:
              result[mac] = (in_addr, {})
            result[mac][1][frame.payload.service] = frame.payload.port
        now = time.monotonic()
    return result

  def get_version(self, mac, addr):
    target = (bytes.fromhex(mac) + bytes(8))[:8]
    self.sequence = (self.sequence + 1) & 0xff
    out_data = protocol.Frame(
      frame_header = protocol.FrameHeader(
        source = self.source
      ),
      frame_address = protocol.FrameAddress(
        target = target,
        res_required = True,
        sequence = self.sequence
      ),
      protocol_header = protocol.ProtocolHeader(
        _type = protocol.PacketType.DEVICE_GET_VERSION
      )
    ).serialize()

    now = time.monotonic()
    timeout = now
    for i in range(GET_VERSION_TRIES):
      self.socket.sendto(out_data, addr)

      timeout += GET_VERSION_TIMEOUT
      while now < timeout:
        r, _, _ = select.select([self.socket], [], [], timeout - now)
        if len(r):
          in_data, in_addr = self.socket.recvfrom(0x1000)
          frame = protocol.Frame()
          frame.deserialize(in_data)
          if (
            in_addr == addr and
            frame.frame_header.protocol == 1024 and
              frame.frame_header.addressable and
              frame.frame_header.source == self.source and
              frame.frame_address.target == target and
              frame.frame_address.sequence == self.sequence and
              frame.protocol_header.type ==
                protocol.PacketType.DEVICE_STATE_VERSION
          ):
            return frame.payload
        now = time.monotonic()
    raise UDPException()

  def set_color(self, mac, addr, hsbk):
    target = (bytes.fromhex(mac) + bytes(8))[:8]
    self.sequence = (self.sequence + 1) & 0xff
    out_data = protocol.Frame(
      frame_header = protocol.FrameHeader(
        source = self.source
      ),
      frame_address = protocol.FrameAddress(
        target = target,
        ack_required = True,
        sequence = self.sequence
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

    now = time.monotonic()
    timeout = now
    for i in range(SET_COLOR_TRIES):
      self.socket.sendto(out_data, addr)

      timeout += SET_COLOR_TIMEOUT
      while now < timeout:
        r, _, _ = select.select([self.socket], [], [], timeout - now)
        if len(r):
          in_data, in_addr = self.socket.recvfrom(0x1000)
          frame = protocol.Frame()
          frame.deserialize(in_data)
          if (
            in_addr == addr and
            frame.frame_header.protocol == 1024 and
              frame.frame_header.addressable and
              frame.frame_header.source == self.source and
              frame.frame_address.target == target and
              frame.frame_address.sequence == self.sequence and
              frame.protocol_header.type ==
                protocol.PacketType.DEVICE_ACKNOWLEDGEMENT
          ):
            return
        now = time.monotonic()
    raise UDPException()

if __name__ == '__main__':
  # demo program to return version of each connected device
  # if run with no arguments it will enumerate all devices
  # if run with at least 1 argument it will enumerate only the given MAC
  # if run with 5 arguments it will also set the colour of the given MAC

  mac = None
  hsbk = None
  if len(sys.argv) >= 2:
    mac = sys.argv[1]
    if len(sys.argv) >= 6:
      import numpy
      hsbk = numpy.array([float(i) for i in sys.argv[2:6]], numpy.double)

  udp = UDP()
  macs = udp.get_service(mac) # may be None
  for mac, (addr, services) in macs.items():
    if protocol.DeviceService.UDP in services:
      version = udp.get_version(mac, addr)
      print('mac', mac, 'vendor', version.vendor, 'product', version.product)
      if hsbk is not None:
        udp.set_color(mac, addr, hsbk)
