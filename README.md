## HSBK <-> RGB conversion utility suite

### Introduction

This has been written to illustrate some points about the LIFX HSBK colour
and how it relates to the SRGB RGB colour space used for common PC monitors.

The utilities are written in Python 3.6+ and are importable as subroutines in
your code. They communicate using `numpy`, so you need to be able to construct
`numpy` arrays before calling the utilities and interpret the result which is
returned as a `numpy` array. There are also command-line versions for testing.

### Utilities

There are 3 basic utilities to try:

* `kelv_to_uv` -- this takes a Kelvin value, which can be in the range 1000 to
  15000, and converts it to a (u, v) value in the CIE 1960 colour space, using
  an approximation by Krystek (see CIE 1960 colour space in Wikipedia).

* `hsbk_to_rgb` -- this takes an HSBK tuple where hue is in degrees, saturation
  and brightness are fractional and Kelvin is in the range 1500..9000, and
  converts to an *approximate* RGB representation, in the SRGB colour space.
  Kelvin below some minimum are outside the SRGB gamut and must be interpreted.

* `rgb_to_hsbk` -- this goes the other way, but the Kelvin value that comes out
  is always 6504. That's because the SRGB colour space has a D65 white point,
  which is close to (but not identical to) 6504K. It is intended that we can
  produce a sensible HSBK value for any RGB, and then convert it back to RGB.

There are also some test programs:

* `inv_test.py` -- checks the RGB -> HSBK -> RGB invertibility for random RGB.

* `image.py` -- creates an image showing all hue and Kelvin combinations, for
  a given saturation and brightness which you specify at the command line.

Finally, there is a program we used in preparing the others, included for
illustrative and maintainability purposes. You could modify this if you want
to use other monitors, not just SRGB monitors. (For example, a Display P3
monitor, or a TV that supports the rec.2020 colour space). If you modify it
you would then re-run it and insert the output into the `hsbk_to_rgb.py` code.

* `primaries.py` -- converts the SRGB primaries into a more convenient matrix.

### Running from the command line

You can run each utility from the command line for testing purposes, e.g.
```
./hsbk_to_rgb.py 60 1 1 3500
```
should produce output similar to the following
```
HSBK (60.000, 1.000000, 1.000000, 3500.000) -> RGB (1.000000, 1.000000, 0.000000)
```

### Importing into your code

You can import the utilities into your own code and call them programmatically.
For example, for the function `kelv_to_uv` you would start by doing this
```
from kelv_to_uv import kelv_to_uv
```
and then you would call the function like this
```
print(kelv_to_uv(3500))
```
which should print something like this (the CIE 1960 u, v coordinates at 3500K)
```
[0.23570687 0.3408642 ]
```

For the more sophisticated subroutines `hsbk_to_rgb()` and `rgb_to_hsbk()` we
recommend that you look in the code of `inv_test.py` or `image.py` as a usage
example. We will give some basic tips here, on the use of `numpy` to call them.

HSBK values are passed as a 4-entry `numpy` array which can be constructed by:
```
hsbk = numpy.array([hue, sat, br, kelv], numpy.double)
```
where `hue`, `sat`, `br`, `kelv` are ordinary Python floating-point values.

RGB values are passed as a 3-entry `numpy` array which can be constructed by:
```
rgb = numpy.array([r, g, b], numpy.double)
```
where `r`, `g`, `b` are ordinary Python floating point values.

You can get back the ordinary Python values by indexing, e.g. `hsbk[0]` gets
you back the hue value. You can print them using Python 3.6+ formatting, e.g.
```
print(f'HSBK ({hsbk[0]:.3f}, {hsbk[1]:.6f}, {hsbk[2]:.6f}, {hsbk[3]:.3f})')
```

The `numpy` RGB values are compatible with Python's `imageio` if you multiply
by 255, round, and then convert to `numpy.uint8`. See the `image.py` for this.

### Caveats and warnings

We have simplified the algorithm as much as possible, because the purpose is
to be *illustrative* and not to produce authoritative outputs for any possible
output device. The code to do this properly, would be much more complicated.

In this code, saturation mixing and brightness scaling is done in gamma-applied
RGB space. This is not really correct, since even the simple act of scaling an
RGB tuple by 50% can corrupt the chromaticity, if you do not unapply the gamma,
scale it, and then re-apply the gamma. But the problem is compatibility, since
the standard HSV space used in e.g., Photoshop, does it in this incorrect way.

The LIFX bulbs attempt to maintain compatibility with the standard space as far
as makes sense. Therefore, we recommend to use this code as a guide. It will
not be perfectly accurate and in particular we do not guarantee that saturation
on the bulbs will behave exactly like (or even similarly to) this program. It
is a guide, and you can further tweak the result as you try it out on the bulb.

Also, I (Nick Downing) have created this program using only publicly available
information, both from Wikipedia and from the summary posted by delfick (also
a LIFX employee) in the thread in LIFX forum here -- at MrMangoo's request:

https://community.lifx.com/t/does-kelvin-have-an-effect-when-saturation-isnt-zero/6698

I have created these utilities in my personal time and they do not represent an
official SDK from LIFX -- they are purely a guide, to illustrate the concepts
explained in the forum post. Having said that, we hope that they are useful.

The code is MIT licensed and you are free to incorporate it into your project.
