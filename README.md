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
available in SRGB, Display P3 and rec.2020 versions. Most PC monitors are SRGB.
Display P3 is an Apple standard with extended colour gamut (a better green
primary). Rec.2020 is an ITU standard for HDTV using pure-wavelength primaries.

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
  converts to a gamma-encoded (R,G,B) value in the SRGB colour space, using
  the 'mired_to_rgb` algorithm as a backend for the Kelvin computation. If you
  don't provide a Kelvin value it will default to 6504K and thus convert an HSV
  tuple as used by Photoshop or Gimp to RGB in a fairly compatible way.

* `hsv_to_rgb` -- this is similar to `rgb_to_hsbk` except that it provides bulk
  conversion of all pixels in an image to produce a new image (usually in PNG
  format). See `rgb_to_hsv` below. Using this utility you can produce a set of
  images at different white points, e.g. take a photo, convert it to HSV, and
  then convert it back to RGB several times specifying different Kelvin values.

* `kelv_to_uv` -- this takes a Kelvin value, which can be in the range 1000 to
  15000, and converts it to a (u,v) value in the CIE 1960 colour space, using
  an approximation by Krystek (see CIE 1960 colour space in Wikipedia).

* `kelv_to_rgb_srgb` -- this takes a Kelvin value, which can be in the range 1000 to
  15000, and converts it to a gamma-encoded (R,G,B) value in the SRGB colour
  space, using the `kelv_to_uv` algorithm as a backend. The result is the same
  as calling `hsbk_to_rgb` with saturation 0 and brightness 1. Kelvin below
  some minimum are outside the SRGB gamut and must be interpreted.

* `mired_to_rgb_srgb` -- this is essentially the same as `kelv_to_rgb` except that
  it takes the argument in mireds (micro reciprocal degrees; equal to 1e6 /
  Kelvin) and directly computes (R,G,B) from mireds instead of going via
  chromaticities and applying various clipping and normalization steps as the
  simpler but slower `kelv_to_rgb` algorithm does. It uses tables of pre-
  computed polynomial approximations to achieve this. It does not have the
  Krystek (u,v) approximation error, but it does introduce its own errors of
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
  considered in the context of (u,v) chromaticity space. We would naively
  think the chromaticity would be halfway between the chromaticities of the
  hue and Kelvin colours, but that isn't the case -- it is affected by several
  factors, including the relative brightnesses of the hue and Kelvin colours
  (e.g. hue of 60 is brighter than 0 or 120 since it has both red and green
  turned on full and thus is the sum of hues 0 and 120), and the corruption
  of chromaticity values that occurs when mixing in a gamma-encoded space.

For the utilities you can use `--device display_p3` to access the Display P3
version, or `--device rec2020` to access the rec.2020 version. (The basic test
programs that only test the result of a single conversion or function call are
given in separate executables for each monitor, whereas the more sophisticated
utilities have all monitors linked into the executable and accept `--device`).

Preparation scripts have been included in `/prepare`. These scripts are meant
to process colorimetric data and formulae and combine them with data from the
SRGB or Display P3 specifications. They produce compact descriptions of the
transformations that will be done by the test programs and callable functions
in `/python`, `/c_float` and `/c_fixed`. This is done through a pipeline that
generates various files `/prepare/*.yml` containing raw data, coefficients,
etc. The `yml` files are language-independent and get compiled into specific
code/data in each langage (Python, C float, C fixed) by `/prepare/*_gen_*.py`.

Raw data for each monitor, that is, the (x,y) chromaticities of each primary
and the white point, are placed in e.g.  `/monitor/srgb/rgbw_to_xy.yml` and
these are processed into a more convenient form during the `make` process.
The processed output is in e.g. `/monitor/srgb/model.yml` and can be tested
using the utilities `/monitor/rgb_to_uvL.py` and `/monitor/uvL_to_rgb.py`.
The '/monitor/*/model.yml` files form inputs to the processing in `/prepare`.

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
For example, for the Kelvins-to-(u,v) conversion you would start by doing this
```
from kelv_to_uv import kelv_to_uv
```
and then you would call the function like this
```
print(kelv_to_uv(3500))
```
which should print something like this (the CIE 1960 u,v coordinates at 3500K)
```
[0.23570687 0.3408642 ]
```

The conversions that depend on the monitor, such as the HSBK-to-RGB and the
RGB-to-HSBK conversions, are implemented as Python objects. That is because the
code which does the conversion, in general the `convert()` method of the
object, is the same for all monitors, and the data needed for the conversion
under a specific monitor is stored in the object. These objects are singleton
objects (as they cannot be modified), and are already instantiated for you.

Once you have imported the correct conversion object, with a line like
```
from hsbk_to_rgb_srgb import hsbk_to_rgb_srgb
```
you need to create a `numpy` array containing the value(s) to be converted,
except when it is a scalar, like in the Kelvins-to-(u,v) example above. Then
you call the `convert()` method of the object, passing in the array, e.g.:
```
import numpy
from hsbk_to_rgb_srgb import hsbk_to_rgb_srgb

hsbk = numpy.array([180, 1, 1, 3500], numpy.double)
rgb = hsbk_to_rgb_srgb.convert(hsbk)
print(rgb)
```
and this would convert `hue = 180`, `sat = 1`, `br = 1`, `kelv = 3500` to RGB.
The result will be returned as a 3-element `numpy` array and the individual
channel values can be accessed by `rgb[0]` for the red channel, and so on.

If you want to be more sophisticated, print them using Python 3.6+ formatting:
```
print(f'HSBK ({hsbk[0]:.3f}, {hsbk[1]:.6f}, {hsbk[2]:.6f}, {hsbk[3]:.3f})')
print(f'RGB ({rgb[0]:.6f}, {rgb[1]:.6f}, {rgb[2]:.6f})')
```

In general the returned RGB values are in gamma-encoded form, and are
compatible with Python's `imageio` if you multiply by 255, round, and then
convert to `numpy.uint8`. See the test programs such as `hue_kelv_test.py`.

If you want to do gamma-decoding, then simply import the functions
`gamma_decode_srgb()` or `gamma_decode_rec2020()`, and similarly for encoding.
They are not implemented as objects and do not have a `convert()` method, this
is because there are not many of them (Display P3 uses SRGB gamma), so it was
not necessary to save code by factoring out the constants for the conversion,
and also they need to be as fast as possible for bulk conversion. For example:
```
from gamma_decode_srgb import gamma_decode_srgb

print(gamma_decode_srgb(.5))
```

### Mathematical optimization

Considerable effort goes into the preparation stage (i.e. when you run `make`
in the `/prepare` directory), to optimize the run-time. For example, the SRGB
gamma-decoding function could have been written from the definition as follows,
```
def gamma_decode_srgb(x):
  return x / 12.92 if x < 12.92 * 0.0031308 else ((x + 0.055) / 1.055) ** 2.4
```
but we do not want to use the `**` operator, equivalently the `powf()` function
in C, and so we do it using a 7th order polynomial approximation as follows,
```
post_factor = numpy.array(
  [
    6.8011762757509715e-03,
    3.5896823593657347e-02,
    1.8946457081379978e-01,
    1.0000000000000000e+00,
    5.2780316430915768e+00
  ],
  numpy.double
)

def gamma_decode_srgb(x):
  if x < 4.0449935999999999e-02:
    return x * 7.7399380804953566e-02
  x, exp = math.frexp(x + 5.5000000000000000e-02)
  assert exp < 2
  y = -1.2846685431737831e-02
  y = y * x + 7.8690715798787891e-02
  y = y * x - 2.3343807254676702e-01
  y = y * x + 6.0014663278898916e-01
  y = y * x + 4.8334165271407381e-01
  y = y * x - 3.9149309063096716e-02
  y = y * x + 2.6705152748352661e-03
  return y * post_factor[exp + 3]
```
In the optimized version we have divided the domain of the curved portion of
the function into 5 sections based on the exponent of the argument, so that we
can prescale the argument, calculate the polynomial, then postscale the result.
This helps the polynomial to fit well, since it only has to fit a small domain.

It should be noted that Python, being an interpreted language, is rather slow,
and so the simpler version using `**` could possibly be preferred when Python
is the target language. (It would probably be faster since it would have less
interpretation overhead, despite that there would be more calculation time).
The C versions should actually be faster using the optimized code, and indeed
there is no `powf()` function for C fixed-point, hence why I have my own way.

Basically, for my projects I need the C fixed-point version, but leaping to the
C fixed-point version is rather difficult, and so it's helpful to have a Python
version to test the algorithm, then a C floating-point version as a halfway
house to the C fixed-point version. This lets me test each part of the design.

If you want the simplest possible Python or C floating-point implementation you
are welcome to restore the `**` or `powf()` functions. An interesting case here
is the `mired_to_rgb` object, whose `convert()` method is able to go directly
from mireds (basically 1e6 divided by Kelvins) to gamma-encoded RGB, by means
of polynomial approximations. If you wanted a simpler approach that only uses
the Krystek Kelvin-to-(u,v) approximation instead of a specifically generated
approximation per monitor, you could do the conversion in two steps, e.g.
```
from kelv_to_uv import kelv_to_uv

class MiredToRGB:
  def __init__(self, uv_to_rgb):
    self.uv_to_rgb = uv_to_rgb

  def convert(self, mired):
    return self.uv_to_rgb.convert(kelv_to_uv(1e6 / mired))
```
With this approach you are still relying on the `uv_to_rgb` object, which is
generated specifically per monitor, but it is straightforward to generate.

### Hue wheel generator

If you are making an app of some kind or a piece of hardware for controlling
the LIFX lights, you will probably want to present a user-interface to let the
user control hue, saturation and Kelvins. With this in mind, I have created a
demo of how this could be done, using the subroutines given above as building
blocks. The code is written on the assumption that we could use our efficient
conversion routines to generate the hue wheel in real time as settings change.

With this in mind, I have created efficient routines, again based on polynomial
approximations, to perform Cartesian-to-polar coordinate conversions. So the
idea is to loop through the pixels in the image, and for each pixel, convert
the Cartesian (x,y) coordinates to polar (r,theta), and then do an HSBK-to-RGB
conversion using the r as the saturation and the theta as the hue.

At present, I have only done a Python prototype of the hue wheel generator. To
do it in C would require porting the efficient trigonometric routines to C (or
using C library routines like `hypotf()` and `atan2f()` if you prefer). On a
modern PC or phone, the hue wheel could be generated in real time like this,
for example if you linked the C code into a Swift application. I'm not sure if
it would be fast enough on a microcontroller. If not, then it may be simpler to
generate the wheel ahead of time using Python, then rotate it onto the display.

To use the hue wheel generator prototype, run it from the command line like:
```
cd python
./hue_wheel.py 180 .5 1 3500 a.png
```
This will generate a wheel with brightness = 1 and Kelvin = 3500, and then
place an indicator in the wheel at position hue = 180 and saturation = .5.
The resultng image can be viewed in `a.png`. It is generated for a 480x272 LCD.

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
