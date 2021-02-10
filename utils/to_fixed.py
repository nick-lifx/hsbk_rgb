import math
from utils.to_hex import to_hex

# returns integer as hex string such that integer * 2 ** exp == n
def to_fixed(n, exp):
  return to_hex(int(round(math.ldexp(n, -exp))))
