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

import re
import sys
import yaml

re_upper = re.compile('([A-Z])')
def camel_to_lower(name):
  words = re_upper.split(name)
  assert words[0] == ''
  return '_'.join(
    [words[i].lower() + words[i + 1] for i in range(1, len(words), 2)]
  )
def camel_to_upper(name):
  words = re_upper.split(name)
  assert words[0] == ''
  return '_'.join(
    [words[i] + words[i + 1].upper() for i in range(1, len(words), 2)]
  )

class Type:
  def __init__(self, size_bytes):
    self.size_bytes = size_bytes
  def default_value(self):
    raise NotImplementedError
  def default_value1(self):
    return self.default_value()
  def default_value2(self, name):
    return name
  def serialize(self, name):
    print(self)
    raise NotImplementedError
  def deserialize(self, indent, name, offset0, offset1):
    raise NotImplementedError
  def write(self, fout):
    pass

# used for expansion of None items from parameter lists, e.g.:
#   def __init__(self, mylist = None)
#     self.mylist = [] if mylist is None else mylist
# this ensures that mutable default values cannot be reused
class TypeMutable(Type):
  def default_value1(self):
    return 'None'
  def default_value2(self, name):
    return f'{self.default_value():s} if {name:s} is None else {name:s}'

class TypeBool(Type):
  def default_value(self):
    return 'False'
  def serialize(self, name):
    return f'int.to_bytes(self.{name:s}, {self.size_bytes:d}, \'little\')'
  def deserialize(self, indent, name, offset0, offset1):
    return f'{indent:s}self.{name} = int.from_bytes(data[{offset0:s}:{offset1:s}], \'little\') != 0\n'

class TypeInt(Type):
  def default_value(self):
    return '0'
  def serialize(self, name):
    return f'int.to_bytes(self.{name:s}, {self.size_bytes:d}, \'little\')'
  def deserialize(self, indent, name, offset0, offset1):
    return f'{indent:s}self.{name} = int.from_bytes(data[{offset0:s}:{offset1:s}], \'little\', True)\n'

class TypeUInt(Type):
  def default_value(self):
    return '0'
  def serialize(self, name):
    return f'int.to_bytes(self.{name:s}, {self.size_bytes:d}, \'little\')'
  def deserialize(self, indent, name, offset0, offset1):
    return f'{indent:s}self.{name} = int.from_bytes(data[{offset0:s}:{offset1:s}], \'little\')\n'

class TypeFloat(Type):
  def default_value(self):
    return '0.'
  def serialize(self, name):
    if self.size_bytes == 4:
      return f'struct.pack(\'<f\', self.{name:s})'
    assert False
  def deserialize(self, indent, name, offset0, offset1):
    if self.size_bytes == 4:
      return f'{indent:s}self.{name} = struct.unpack(\'<f\', data[{offset0:s}:{offset1:s}])\n'
    assert False

class TypeByte(Type):
  def default_value(self):
    return 'b\'\\0\''

class TypeEnum(TypeUInt):
  # values is a dict of {name: value} where name is string, value is int
  def __init__(self, size_bytes, name, values):
    Type.__init__(self, size_bytes)
    self.name = name
    self.values = values
  def default_value(self):
    return f'{self.name:s}.{list(self.values.keys())[0]}'
  def write(self, fout):
    fout.write(
      '''class {0:s}(Enum):
{1:s}'''.format(
        self.name,
        (
          '  pass\n'
        if len(self.values) == 0 else
          ''.join(
            [
              f'  {name:s} = {value:d}\n'
              for name, value in self.values.items()
            ]
          )
        )
      )
    )

class TypeArray(TypeMutable):
  def __init__(self, size_bytes, dim, _type):
    TypeMutable.__init__(self, size_bytes)
    self.dim = dim
    self.type = _type
  def default_value(self):
    return (
      f'bytes({self.dim:d})'
    if isinstance(self.type, TypeByte) else
      f'{self.dim:d} * [{self.type.default_value():s}]'
    )
  def default_value1(self):
    return (
      Type.default_value1(self)
    if isinstance(self.type, TypeByte) else
      TypeMutable.default_value1(self)
    )
  def default_value2(self, name):
    return (
      Type.default_value2(self, name)
    if isinstance(self.type, TypeByte) else
      TypeMutable.default_value2(self, name)
    )
  def serialize(self, name):
    return (
      f'self.{name:s}'
    if isinstance(self.type, TypeByte) else
      f'b\'\'.join([i.serialize() for i in self.{name:s}])'
    )
  def deserialize(self, indent, name, offset0, offset1):
    return (
      f'{indent:s}self.{name:s} = data[{offset0:s}:{offset1:s}]\n'
    if isinstance(self.type, TypeByte) else
      '''{0:s}for i in range({1:d}):
{2:s}'''.format(
        indent,
        self.dim,
        self.type.deserialize(
          f'{indent:s}  ',
          f'{name:s}[i]',
          f'{offset0:s} + i * {self.type.size_bytes:d}',
          f'{offset0:s} + i * {self.type.size_bytes:d} + {self.type.size_bytes:d}'
        )
      )
    )

class TypeStruct(TypeMutable):
  # fields is a dict of {name: type} where name is string, type is Type
  def __init__(self, size_bytes, name, fields):
    TypeMutable.__init__(self, size_bytes)
    self.name = name
    self.fields = fields
  def default_value(self):
    return f'{self.name:s}()'
  def write(self, fout):
    empty = all(
      [isinstance(_type, TypeReserved) for _type in self.fields.values()]
    )
    offset = 0
    offsets = {}
    for name, _type in self.fields.items():
      offsets[name] = offset
      offset += _type.size_bytes
    assert offset == self.size_bytes
    fout.write(
      '''class {0:s}(Struct):
  def __init__(
    self{1:s}
  ):
{2:s}  def serialize(self):
    return b''.join(
      [{3:s}
      ]
    )
  def deserialize(self, data):
{4:s}'''.format(
        self.name,
        ''.join(
          [
            f',\n    {name:s} = {_type.default_value1():s}'
            for name, _type in self.fields.items()
            if not isinstance(_type, TypeReserved)
          ]
        ),
        (
          '    pass\n'
        if empty else
          ''.join(
            [
              f'    self.{name:s} = {_type.default_value2(name):s}\n'
              for name, _type in self.fields.items()
              if not isinstance(_type, TypeReserved)
            ]
          )
        ),
        ','.join(
          [
            f'\n        {_type.serialize(name):s}'
            for name, _type in self.fields.items()
          ]
        ),
        (
          '    pass\n'
        if empty else
          ''.join(
            [
              _type.deserialize(
                '    ',
                name, 
                str(offsets[name]),
                str(offsets[name] + _type.size_bytes)
              )
              for name, _type in self.fields.items()
              if not isinstance(_type, TypeReserved)
            ]
          )
        )
      )
    )
  def serialize(self, name):
    return f'self.{name:s}.serialize()'
  def deserialize(self, indent, name, offset0, offset1):
    return f'{indent:s}self.{name:s}.deserialize(data[{offset0:s}:{offset1:s}])\n'

class TypeReserved(Type):
  # placeholder for fields that do not appear in field list but take space
  def serialize(self, name):
    return f'bytes({self.size_bytes:d})'

types = {
  'bool': TypeBool(1),
  'int8': TypeInt(1),
  'int16': TypeInt(2),
  'int32': TypeInt(4),
  'int64': TypeInt(8),
  'uint8': TypeUInt(1),
  'uint16': TypeUInt(2),
  'uint32': TypeUInt(4),
  'uint64': TypeUInt(8),
  'float32': TypeFloat(4),
  'float64': TypeFloat(8),
  'byte': TypeByte(1)
}
re_array = re.compile('\[([0-9]+)\]')
def gen_type(type_str):
  match = re_array.match(type_str)
  if match is not None:
    dim = int(match.group(1))
    _type = gen_type(type_str[len(match.group(0)):])
    return TypeArray(dim * _type.size_bytes, dim, _type)
  _type = types.get(type_str)
  if _type is None:
    # forward reference, hope it will be filled in later
    #print('warning: forward reference:', type_str)
    _type = TypeStruct(0, None, {})
    types[type_str] = _type
  return _type

protocol = yaml.safe_load(sys.stdin)

for name, data in protocol['enums'].items():
  _type = gen_type(data['type'])
  assert isinstance(_type, TypeUInt)
  size_bytes = _type.size_bytes

  prefix = camel_to_upper(name) + '_'
  values = {}
  for item in data['values']:
    item_name = item['name']
    if item_name != 'reserved':
      assert item_name[:len(prefix)] == prefix
      values[item_name[len(prefix):]] = item['value']

  key = f'<{name:s}>'
  assert key not in types
  types[f'<{name:s}>'] = TypeEnum(size_bytes, name, values)

for name, data in protocol['fields'].items():
  size_bytes = data['size_bytes']

  fields = {}
  reserved_index = 0
  for item in data['fields']:
    _type = item['type']
    if _type == 'reserved':
      fields[f'reserved{reserved_index:d}'] = TypeReserved(item['size_bytes'])
      reserved_index += 1
    else:
      fields[camel_to_lower(item['name'])] = gen_type(_type)

  # make sure we fill in a forward reference if there is one
  key = f'<{name:s}>'
  _type = types.get(key)
  if _type is None:
    _type = TypeStruct(0, None, {})
    types[key] = _type
  assert isinstance(_type, TypeStruct) and _type.name is None
  _type.size_bytes = size_bytes
  _type.name = name
  _type.fields = fields

packet_types = {}
packet_type_to_type = {}
for _, data in protocol['packets'].items():
  for packet_name, packet_data in data.items():
    enum_packet_name = camel_to_upper(packet_name)
    packet_types[enum_packet_name] = packet_data['pkt_type']

    size_bytes = packet_data['size_bytes']

    fields = {}
    reserved_index = 0
    for item in packet_data['fields']:
      _type = item['type']
      if _type == 'reserved':
        fields[f'reserved{reserved_index:d}'] = TypeReserved(item['size_bytes'])
        reserved_index += 1
      else:
        fields[camel_to_lower(item['name'])] = gen_type(_type)

    if len(fields):
      # make sure we fill in a forward reference if there is one
      key = f'<{packet_name:s}>'
      _type = types.get(key)
      if _type is None:
        _type = TypeStruct(0, None, {})
        types[key] = _type
      assert isinstance(_type, TypeStruct) and _type.name is None
      _type.size_bytes = size_bytes
      _type.name = packet_name
      _type.fields = fields

      packet_type_to_type[enum_packet_name] = packet_name
types['PacketType'] = TypeEnum(2, 'PacketType', packet_types)

prefix = ''
for _type in types.values():
  if isinstance(_type, TypeEnum) or isinstance(_type, TypeStruct):
    sys.stdout.write(prefix)
    _type.write(sys.stdout)
    prefix = '\n'
sys.stdout.write(
  '''
packet_type_to_type = {{{0:s}
}}
'''.format(
    ','.join(
      [
        f'\n  PacketType.{enum_packet_name:s}: {packet_name:s}'
        for enum_packet_name, packet_name in packet_type_to_type.items()
      ]
    )
  )
)
