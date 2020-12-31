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

# mpmath can't convert an empty list to a vector
# it seems to be trying to determine cols from first list entry
def vector(x):
  return mpmath.matrix(x) if len(x) else mpmath.matrix(0, 1)

def add(p, q):
  a = p.rows
  b = q.rows
  r = mpmath.matrix(max(a, b), 1)
  r[:a] = p
  r[:b] += q
  return r

def mul(p, q):
  a = p.rows
  b = q.rows
  r = mpmath.matrix(a + b - 1, 1)
  for i in range(a):
    for j in range(b):
      r[i + j] += p[i] * q[j]
  return r

def deriv(p):
  return vector([p[i] * i for i in range(1, p.rows)])

def eval(p, x):
  # Horner's rule
  y = mpmath.mpf(0.)
  for i in range(p.rows - 1, -1, -1):
    y = y * x + p[i]
  return y

def eval_multi(p, x):
  # Horner's rule
  y = mpmath.matrix(x.rows, 1)
  for i in range(p.rows - 1, -1, -1):
    y = vector([y[i] * x[i] for i in range(x.rows)]) + p[i]
  return y

def compose(p, x):
  # Horner's rule where x is a polynomial
  y = p[p.rows - 1:]
  for i in range(p.rows - 2, -1, -1):
    y = mul(y, x)
    y[0] += p[i]
  return y

# this has no protection from division by zero
# it should only be called when properties of function are known in advance
def newton(p, x, iters = 10):
  p_deriv = deriv(p)
  for i in range(iters):
    x -= eval(p, x) / eval(p_deriv, x)
    print('i', i, 'x', x, 'p(x)', eval(p, x))
  return x

def newton_multi(p, x, iters = 10):
  p_deriv = deriv(p)
  for i in range(iters):
    x -= eval_multi(p, x) / eval_multi(p_deriv, x)
    print('i', i, 'x', x, 'p(x)', eval_multi(p, x))
  return x

def real_root(p, p_deriv, a, b, increasing):
  #print('real_root: p', p, 'p_deriv', p_deriv)
  #y_a = eval_multi(p, a)
  #y_b = eval_multi(p, b)
  #print('a', a, 'p(a)', y_a, 'b', b, 'p(b)', y_b, 'increasing', increasing)
  #assert (y_a <= 0. and y_b > 0.) if increasing else (y_a >= 0 and y_b < 0.)
  x = .5 * (a + b)
  for i in range(15):
    y = eval(p, x)
    #print('i', i, 'x', x, 'p(x)', y)
    if y < 0.:
      y1 = eval(p_deriv, x)
      if y1 < 0.:
        # x - y / y1 > a <=> y / y1 < x - a <=> y > (x - a) y1
        if y > (x - a) * y1:
          x1 = x - y / y1
          if x1 > a:
            x = x1
            continue
      elif y1 > 0.:
        # x - y / y1 < b <=> y / y1 > x - b <=> y > (x - b) y1
        if y > (x - b) * y1:
          x1 = x - y / y1
          if x1 < b:
            x = x1
            continue
      if increasing:
        # p(x) < 0 and p(b) >= 0
        a = x
      else:
        # p(a) >= 0 and p(x) < 0
        b = x
    elif y > 0.:
      y1 = eval(p_deriv, x)
      if y1 < 0.:
        # x - y / y1 < b <=> y / y1 > x - b <=> y < (x - b) y1
        if y < (x - b) * y1:
          x1 = x - y / y1
          if x1 < b:
            x = x1
            continue
      elif y1 > 0.:
        # x - y / y1 > a <=> y / y1 < x - a <=> y < (x - a) y1
        if y < (x - a) * y1:
          x1 = x - y / y1
          if x1 > a:
            x = x1
            continue
      if increasing:
        # p(a) < 0 and p(x) > 0
        b = x
      else:
        # p(x) > 0 and p(b) <= 0
        a = x
    else:
      break
    #print('reset: a', a, 'b', b)
    x = .5 * (a + b)
  return x

def real_roots(p, a, b):
  # see https://www.researchgate.net/publication/320864673_A_simple_algorithm_to_find_all_real_roots_of_a_polynomial
  n = p.rows
  while n > 0 and p[n - 1] == 0.:
    n -= 1
  #print('real_roots: n', n)
  out = [a]
  if n >= 2:
    if n == 2:
      # a + b x = 0 => x = -a / b
      x = -p[0] / p[1]
      if x > a and x < b:
        out.append(x)
    else:
      p = p[:n]
      p_deriv = deriv(p)
      x = real_roots(p_deriv, a, b)
      #print('x', x)
      #print('p\'(x)', eval_multi(p_deriv, x))
      y = eval_multi(p, x)
      #print('p(x)', y)
      for i in range(x.rows - 1):
        if y[i + 1] < 0.:
          if y[i] >= 0.:
            out.append(real_root(p, p_deriv, x[i], x[i + 1], False))
        elif y[i + 1] > 0.:
          if y[i] <= 0.:
            out.append(real_root(p, p_deriv, x[i], x[i + 1], True))
        else:
          out.append(x[i + 1])
  if out[-1] < b:
    out.append(b)
  #print('real_roots: n', n, 'returning', mpmath.matrix(out))
  return mpmath.matrix(out)

def extrema(p, a, b):
  x = real_roots(deriv(p), a, b)
  return x, eval_multi(p, x)

# returns the extrema of a list of contiguous intervals of x
# similar to calling extrema() on each interval, but more efficient
def interval_extrema(p, interval_x):
  n_intervals = interval_x.rows - 1
  extrema_x, extrema_y = extrema(p, interval_x[0], interval_x[n_intervals])
  #print('extrema_x', extrema_x)
  #print('extrema_y', extrema_y)
  #print('interval_x', interval_x)
  interval_y = eval_multi(p, interval_x) # first and last will match extrema_y
  #print('interval_y', interval_y)
  out = []
  j = 1
  for i in range(n_intervals):
    k = j
    while extrema_x[k] < interval_x[i + 1]:
      k += 1
    out.append(
      (
        mpmath.matrix(
          [interval_x[i]] + list(extrema_x[j:k]) + [interval_x[i + 1]]
        ),
        mpmath.matrix(
          [interval_y[i]] + list(extrema_y[j:k]) + [interval_y[i + 1]]
        )
      )
    )
    j = k
  return out

def _range(p, a, b):
  _, y = extrema(p, a, b)
  return min(y), max(y)
