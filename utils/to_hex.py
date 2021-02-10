def to_hex(n):
  return (
    str(n)
  if n >= -9 and n < 10 else
    f'0x{n:x}'
  if n >= 0 else
    f'-0x{-n:x}'
  )
