import numpy
import numpy.linalg

EPSILON = 1e-12

def add(p, q):
  a = p.shape[0]
  b = q.shape[0]
  r = numpy.zeros((max(a, b),), numpy.double)
  r[:a] = p
  r[:b] += q
  return r

def mul(p, q):
  a = p.shape[0]
  b = q.shape[0]
  r = numpy.zeros((a + b - 1,), numpy.double)
  for i in range(b):
    r[i:i + a] += q[i:i + 1] * p
  return r

def deriv(p):
  return p[1:] * numpy.arange(1, p.shape[0], dtype = numpy.int32)

def eval(p, x):
  # Horner's rule
  y = numpy.zeros_like(x)
  for i in range(p.shape[0] - 1, -1, -1):
    y = y * x + p[i]
  return y

def compose(p, x):
  # Horner's rule where x is a polynomial
  y = p[-1:]
  for i in range(p.shape[0] - 2, -1, -1):
    y = mul(y, x)
    y[0] += p[i]
  return y

# works, not used at the moment (isn't as numerically stable as I would like)
#def roots(p, epsilon = EPSILON):
#  # return eigenvalues of the companion matrix
#  n = p.shape[0]
#  while n > 0 and abs(p[n - 1]) < epsilon:
#    n -= 1
#  if n < 2:
#    return p[:n]
#  c = numpy.zeros((n - 1, n - 1), numpy.double)
#  c[1:, :-1] = numpy.identity(n - 2, numpy.double)
#  c[:, -1] = -p[:n - 1] / p[n - 1]
#  return numpy.linalg.eigvals(c)

# this has no protection from division by zero
# it should only be called when properties of function are known in advance
def newton(p, x, iters = 10):
  p_deriv = deriv(p)
  for i in range(iters):
    x -= eval(p, x) / eval(p_deriv, x)
    print('i', i, 'x', x, 'p(x)', eval(p, x))
  return x

def real_root(p, p_deriv, a, b, increasing):
  #print('real_root: p', p, 'p_deriv', p_deriv)
  #y_a = eval(p, a)
  #y_b = eval(p, b)
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

def real_roots(p, a, b, epsilon = EPSILON):
  # see https://www.researchgate.net/publication/320864673_A_simple_algorithm_to_find_all_real_roots_of_a_polynomial
  n = p.shape[0]
  while n > 0 and abs(p[n - 1]) < epsilon:
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
      x = real_roots(p_deriv, a, b, epsilon)
      #print('x', x)
      #print('p\'(x)', eval(p_deriv, x))
      y = eval(p, x)
      #print('p(x)', y)
      for i in range(x.shape[0] - 1):
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
  #print('real_roots: n', n, 'returning', numpy.array(out, numpy.double))
  return numpy.array(out, numpy.double)

def extrema(p, a, b, epsilon = EPSILON):
  x = real_roots(deriv(p), a, b, epsilon)
  return x, eval(p, x)

# returns the extrema of a list of contiguous intervals of x
# similar to calling extrema() on each interval, but more efficient
def interval_extrema(p, interval_x, epsilon = EPSILON):
  n_intervals = interval_x.shape[0] - 1
  extrema_x, extrema_y = extrema(p, interval_x[0], interval_x[-1], epsilon)
  #print('extrema_x', extrema_x)
  #print('extrema_y', extrema_y)
  #print('interval_x', interval_x)
  interval_y = eval(p, interval_x) # first and last will match extrema_y
  #print('interval_y', interval_y)
  out = []
  j = 1
  for i in range(n_intervals):
    k = j
    while extrema_x[k] < interval_x[i + 1]:
      k += 1
    out.append(
      (
        numpy.array(
          [interval_x[i]] + list(extrema_x[j:k]) + [interval_x[i + 1]],
          numpy.double
        ),
        numpy.array(
          [interval_y[i]] + list(extrema_y[j:k]) + [interval_y[i + 1]],
          numpy.double
        )
      )
    )
    j = k
  return out

def _range(p, a, b, epsilon = EPSILON):
  _, y = extrema(p, a, b, epsilon)
  return numpy.min(y), numpy.max(y)
