## HSBK <-> RGB conversion utility suite

### Introduction

This has been written to illustrate some points about the LIFX HSBK colour
space and how it relates to the SRGB RGB colour space used for common PC
monitors.

The utilities are written in Python 3.6+ and are importable as subroutines in
your code. They communicate using `numpy`, so you need to be able to construct
`numpy` arrays before calling the utilities, and interpret the result which is
returned as a `numpy` array. There are also command-line versions for testing.

There are also C versions of each utility and subroutine. The C versions come
in two flavours, the "regular" flavour uses `float` to represent the HSBK and
RGB tuples whereas the "fixed-point" flavour uses `int32_t`. The fixed-point
version is much more advanced and is intended for microcontrollers without FPU.

The fixed-point versions of the command-line utilities should work more or less
the same as the regular versions, since they contain inbuilt conversion between
floating and fixed point. The fixed-point callable subroutines only deal with
`int32_t` and each subroutine has a comment in the code explaining the scaling.

The conversions which are sensitive to the colour space in use (essentially
those which take a Kelvin value and hence must compute the Kelvin locus) are
available in SRGB and Display P3 versions. Most PC monitors are SRGB. Display
P3 is an Apple standard with extended colour gamut (a better green primary).

### Building

After checking out the repository you should execute `make` at the top level.
This will build the `prepare` subdirectory first and then the others (`python`,
`c_float` and `c_fixed`). Before building you need to have `python3`, `gcc`,
and `libpng` installed. Your Python installation must be 3.6+ and have `numpy`
and `imageio`. (Note: These dependencies may not be exhaustive going forward).

### Utilities

There are a number of command-line utilities to try:

* `hsbk_to_rgb_srgb` -- this takes an HSBK tuple where hue is in degrees, saturation
  and brightness are fractional and Kelvin is in the range 1500 to 9000, and
  converts to a gamma-encoded (R, G, B) value in the SRGB colour space, using
  the 'mired_to_rgb` algorithm as a backend for the Kelvin computation. If you
  don't provide a Kelvin value it will default to 6504K and thus convert an HSV
  tuple as used by Photoshop or Gimp to RGB in a fairly compatible way.

* `hsv_to_rgb` -- this is similar to `rgb_to_hsbk` except that it provides bulk
  conversion of all pixels in an image to produce a new image (usually in PNG
  format). See `rgb_to_hsv` below. Using this utility you can produce a set of
  images at different white points, e.g. take a photo, convert it to HSV, and
  then convert it back to RGB several times specifying different Kelvin values.

* `kelv_to_uv` -- this takes a Kelvin value, which can be in the range 1000 to
  15000, and converts it to a (u, v) value in the CIE 1960 colour space, using
  an approximation by Krystek (see CIE 1960 colour space in Wikipedia).

* `kelv_to_rgb_srgb` -- this takes a Kelvin value, which can be in the range 1000 to
  15000, and converts it to a gamma-encoded (R, G, B) value in the SRGB colour
  space, using the `kelv_to_uv` algorithm as a backend. The result is the same
  as calling `hsbk_to_rgb` with saturation 0 and brightness 1. Kelvin below
  some minimum are outside the SRGB gamut and must be interpreted.

* `mired_to_rgb_srgb` -- this is essentially the same as `kelv_to_rgb` except that
  it takes the argument in mireds (micro reciprocal degrees; equal to 1e6 /
  Kelvin) and directly computes (R, G, B) from mireds instead of going via
  chromaticities and applying various clipping and normalization steps as the
  simpler but slower `kelv_to_rgb` algorithm does. It uses tables of pre-
  computed polynomial approximations to achieve this. It does not have the
  Krystek (u, v) approximation error, but it does introduce its own errors of
  about the same magnitude, so results differ slightly from `kelv_to_rgb`.

* `rgb_to_hsbk_srgb` -- this is the inverse conversion to `hsbk_to_rgb_srgb` and should
  be lossless, except to say that you must provide a Kelvin value to use in the
  conversion. When converting HSBK to RGB and back to HSBK, it will produce an
  HSBK with the same eyeball colour as originally, but it may be expressed
  differently if you don't provide the same original Kelvin as the white point.
  If you don't provide a Kelvin value it will default to 6504K and thus convert
  an RGB tuple to HSV as used by Photoshop or Gimp in a fairly compatible way.

* `rgb_to_hsv` -- this is similar to `rgb_to_hsbk` except that it provides bulk
  conversion of all pixels in an image to produce a new image (usually in PNG
  format). On the HSV side it uses an unusual image format where the hue is
  encoded into the red value, the saturation into the green value, and the
  brightness into the blue value. It is still possible to make out the original
  image details when the HSV image is viewed in a standard viewer. HSV images
  do not store a Kelvin value per pixel and you provide one on the command line
  which is then applied to all pixels. This gives control over the white point
  of the image in a similar way to Gimp or Photoshop's white point adjustment.

* `gamma_decode_srgb` -- takes a single fractional value (0 to 1) and gamma
  decodes it according to the SRGB gamma function, using a shorthand convention
  that "decoding" means taking a gamma-compressed value as would occur in a PNG
  file and converting it to a linear intensity for an output device.

* `gamma_encode_srgb` -- takes a single fractional value (0 to 1) and gamma
  encodes it according to the SRGB gamma function, the opposite of the above.

Note that the `*_srgb` utilities in general have a corresponding `*_display_p3`
utility which uses a different Kelvin locus that is accurate on a Display P3
monitor. An exception is the gamma decode/encode which use the SRGB version
for Display P3 (since Display P3 is specified to have the same gamma as SRGB).

There are also some test programs:

* `hue_kelv_test` -- creates an image showing hue and Kelvin combinations,
  for a given saturation and brightness which you specify at the command line.

* `inv_test` -- checks the RGB -> HSBK -> RGB invertibility for random RGB.

* `sat_test` -- creates an image similar to the result of `hue_kelv_test` with
  with saturation 0.5 and brightness 1, but the image is further processed to
  investigate how the saturation of 0.5 combines the hue and Kelvin when
  considered in the context of (u, v) chromaticity space. We would naively
  think the chromaticity would be halfway between the chromaticities of the
  hue and Kelvin colours, but that isn't the case -- it is affected by several
  factors, including the relative brightnesses of the hue and Kelvin colours
  (e.g. hue of 60 is brighter than 0 or 120 since it has both red and green
  turned on full and thus is the sum of hues 0 and 120), and the corruption
  of chromaticity values that occurs when mixing in a gamma-encoded space.

For the utilities you can use `--device display_p3` to access the Display P3
version. (Both SRGB and Display P3 subroutines are linked into the executable).

Preparation scripts have been included in `prepare/`. These scripts are meant
to process colorimetric data and formulae and combine them with data from the
SRGB or Display P3 specifications. They produce compact descriptions of the
transformations that will be done by the test programs and callable functions
in `python/`, `c_float/` and `c_fixed/`. This is done through a pipeline that
generates various files like `prepare/*.yml` containing raw data, coefficients,
etc. The `yml` files are language-independent and get compiled into specific
code in each langage (Python, C float, C fixed) e.g. by `prepare/*_gen_py.py`.

### Running from the command line

You can run each utility from the command line for testing purposes, e.g.
```
cd python
./hsbk_to_rgb_srgb.py 60 1 1 3500
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

For the more sophisticated subroutines `hsbk_to_rgb_srgb()` and `rgb_to_hsbk_srgb()` we
recommend that you look in the code of `hue_kelv_test.py` or `inv_test.py` as a usage
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

In general the returned RGB values are in gamma-encoded form, and are
compatible with Python's `imageio` if you multiply by 255, round, and then
convert to `numpy.uint8`. See the test programs such as `hue_kelv_test.py`.

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
