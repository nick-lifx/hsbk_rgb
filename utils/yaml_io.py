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

import mpmath
import numpy
import yaml

def read_file(path):
  with open(path) as fin:
    return yaml.safe_load(fin)

def write_file(path, data):
  with open(path, 'w') as fout:
    yaml.dump(data, fout)

RANK_BOOL = 0
RANK_INT = 1
RANK_FLOAT = 2
RANK_STR = 3
rank_to_type = [numpy.bool_, numpy.int32, numpy.double, mpmath.mpf]
def _import(data, rank_to_type_override = {}):
  def wrap(scanned_data):
    data, rank = scanned_data
    _type = rank_to_type_override.get(rank, rank_to_type[rank])
    return (
      (
        numpy.array(data, _type)
      if issubclass(_type, numpy.generic) else
        mpmath.matrix(data)
      if _type == mpmath.mpf else
        data
      )
    if isinstance(data, list) else
      data
    if isinstance(data, dict) else
      (
        data # avoid using numpy scalars
      if issubclass(_type, numpy.generic) else
        _type(data)
      )
    )
  def scan(data):
    # scalars and lists do not call wrap() yet
    # for scalars we want to avoid conversion to numpy if not in a list
    # for lists we want to do conversion after collecting all nested lists
    if isinstance(data, bool):
      return data, RANK_BOOL
    if isinstance(data, int):
      return data, RANK_INT
    if isinstance(data, float):
      return data, RANK_FLOAT
    if isinstance(data, str):
      return data, RANK_STR
    if isinstance(data, list):
      scanned_data = [scan(i) for i in data]
      return (
        [i for i, _ in scanned_data],
        max([i for _, i in scanned_data])
      )
    if isinstance(data, dict):
      scanned_data = [(i, scan(j)) for i, j in data.items()]
      return (
        {i: wrap(j) for i, j in scanned_data},
        max([i for _, (_, i) in scanned_data])
      )
    assert False
  return wrap(scan(data))

def export(data):
  return (
    float(data)
  if isinstance(data, numpy.floating) else
    int(data)
  if isinstance(data, numpy.integer) else
    bool(data)
  if isinstance(data, numpy.bool_) else
    [export(i) for i in data]
  if isinstance(data, numpy.ndarray) else
    str(data)
  if isinstance(data, mpmath.mpf) else
    (
      [export(data[i]) for i in range(data.rows)]
    if data.cols == 1 else
      [
        [export(data[i, j]) for j in range(data.cols)]
        for i in range(data.rows)
      ]
    )
  if isinstance(data, mpmath.matrix) else
    {i: export(j) for i, j in data.items()}
  if isinstance(data, dict) else
    data
  )

if __name__ == '__main__':
  mpmath.mp.prec = 106

  write_file(
    'a.yml',
    export(
      {
        'a': True,
        'b': 27,
        'c': 27.5,
        'd': '27.5000000000000000000000000000001',
        'e': numpy.array([True, False, True], numpy.bool),
        'f': numpy.array([[1, 2, 3]], numpy.int32),
        'g': numpy.array([[1., 2., 3.], [4., 5., 6.]], numpy.double),
        'h': mpmath.matrix([[1., 2., 3.], [4., 5., 6.]]),
        'i': mpmath.matrix([1., 2., '3.0000000000000000000000000001'])
      }
    )
  )
  print(_import(read_file('a.yml')))
