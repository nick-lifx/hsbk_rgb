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

all: \
srgb_gamma_decode.gen_py \
srgb_gamma_decode.gen_c_float \
srgb_gamma_decode.gen_c_fixed \
srgb_gamma_encode.gen_py \
srgb_gamma_encode.gen_c_float \
srgb_gamma_encode.gen_c_fixed \
srgb_uv_to_rgb.gen_py \
srgb_uv_to_rgb.gen_c_fixed \
srgb_uv_to_rgb.gen_c_float \
srgb_rgb_to_uv.gen_py \
srgb_rgb_to_uv.gen_c_fixed \
srgb_rgb_to_uv.gen_c_float \
srgb_mired_to_rgb.gen_py \
srgb_mired_to_rgb.gen_c_float \
srgb_mired_to_rgb.gen_c_fixed \
display_p3_uv_to_rgb.gen_py \
display_p3_uv_to_rgb.gen_c_fixed \
display_p3_uv_to_rgb.gen_c_float \
display_p3_rgb_to_uv.gen_py \
display_p3_rgb_to_uv.gen_c_fixed \
display_p3_rgb_to_uv.gen_c_float \
display_p3_mired_to_rgb.gen_py \
display_p3_mired_to_rgb.gen_c_float \
display_p3_mired_to_rgb.gen_c_fixed \
rtheta_to_xy.gen_py \
xy_to_rtheta.gen_py \
kelv_to_uv.gen_c_fixed

srgb_gamma_decode.gen_py: srgb_gamma_decode_fit.yml
	./gamma_decode_gen_py.py $^ >$@

srgb_gamma_decode.gen_c_fixed: srgb_gamma_decode_fit.yml
	./gamma_decode_gen_c_fixed.py $^ >$@

srgb_gamma_decode.gen_c_float: srgb_gamma_decode_fit.yml
	./gamma_decode_gen_c_float.py $^ >$@

srgb_gamma_decode_fit.yml:
	./gamma_decode_fit.py $^ $@

srgb_gamma_encode.gen_py: srgb_gamma_encode_fit.yml
	./gamma_encode_gen_py.py $^ >$@

srgb_gamma_encode.gen_c_fixed: srgb_gamma_encode_fit.yml
	./gamma_encode_gen_c_fixed.py $^ >$@

srgb_gamma_encode.gen_c_float: srgb_gamma_encode_fit.yml
	./gamma_encode_gen_c_float.py $^ >$@

srgb_gamma_encode_fit.yml:
	./gamma_encode_fit.py $^ $@

srgb_uv_to_rgb.gen_py: srgb_primaries.yml
	./uv_to_rgb_gen_py.py $^ >$@

srgb_uv_to_rgb.gen_c_fixed: srgb_primaries.yml
	./uv_to_rgb_gen_c_fixed.py $^ >$@

srgb_uv_to_rgb.gen_c_float: srgb_primaries.yml
	./uv_to_rgb_gen_c_float.py $^ >$@

srgb_rgb_to_uv.gen_py: srgb_primaries.yml
	./rgb_to_uv_gen_py.py $^ >$@

srgb_rgb_to_uv.gen_c_fixed: srgb_primaries.yml
	./rgb_to_uv_gen_c_fixed.py $^ >$@

srgb_rgb_to_uv.gen_c_float: srgb_primaries.yml
	./rgb_to_uv_gen_c_float.py $^ >$@

srgb_primaries.yml: srgb_rgbw_to_xy.yml
	./primaries.py $^ $@

srgb_mired_to_rgb.gen_py: srgb_mired_to_rgb_fit.yml
	./mired_to_rgb_gen_py.py $^ >$@

srgb_mired_to_rgb.gen_c_float: srgb_mired_to_rgb_fit.yml
	./mired_to_rgb_gen_c_float.py $^ >$@

srgb_mired_to_rgb.gen_c_fixed: srgb_mired_to_rgb_fit.yml
	./mired_to_rgb_gen_c_fixed.py $^ >$@

srgb_mired_to_rgb_fit.yml: srgb_primaries.yml
	./mired_to_rgb_fit.py $^ 150 500 $@

display_p3_uv_to_rgb.gen_py: display_p3_primaries.yml
	./uv_to_rgb_gen_py.py $^ >$@

display_p3_uv_to_rgb.gen_c_fixed: display_p3_primaries.yml
	./uv_to_rgb_gen_c_fixed.py $^ >$@

display_p3_uv_to_rgb.gen_c_float: display_p3_primaries.yml
	./uv_to_rgb_gen_c_float.py $^ >$@

display_p3_rgb_to_uv.gen_py: display_p3_primaries.yml
	./rgb_to_uv_gen_py.py $^ >$@

display_p3_rgb_to_uv.gen_c_fixed: display_p3_primaries.yml
	./rgb_to_uv_gen_c_fixed.py $^ >$@

display_p3_rgb_to_uv.gen_c_float: display_p3_primaries.yml
	./rgb_to_uv_gen_c_float.py $^ >$@

display_p3_primaries.yml: display_p3_rgbw_to_xy.yml
	./primaries.py $^ $@

display_p3_mired_to_rgb.gen_py: display_p3_mired_to_rgb_fit.yml
	./mired_to_rgb_gen_py.py $^ >$@

display_p3_mired_to_rgb.gen_c_float: display_p3_mired_to_rgb_fit.yml
	./mired_to_rgb_gen_c_float.py $^ >$@

display_p3_mired_to_rgb.gen_c_fixed: display_p3_mired_to_rgb_fit.yml
	./mired_to_rgb_gen_c_fixed.py $^ >$@

display_p3_mired_to_rgb_fit.yml: display_p3_primaries.yml
	./mired_to_rgb_fit.py $^ 150 950 $@

rtheta_to_xy.gen_py: rtheta_to_xy_fit.yml
	./rtheta_to_xy_gen_py.py $^ >$@

rtheta_to_xy_fit.yml:
	./rtheta_to_xy_fit.py $^ $@

xy_to_rtheta.gen_py: xy_to_rtheta_fit.yml
	./xy_to_rtheta_gen_py.py $^ >$@

xy_to_rtheta_fit.yml:
	./xy_to_rtheta_fit.py $^ $@

kelv_to_uv.gen_c_fixed:
	./kelv_to_uv_gen_c_fixed.py >$@

clean:
	rm -f \
*.gen_py \
*.gen_c_fixed \
*.gen_c_float \
srgb_gamma_decode_fit.yml \
srgb_gamma_encode_fit.yml \
srgb_primaries.yml \
srgb_mired_to_rgb_fit.yml \
display_p3_primaries.yml \
display_p3_mired_to_rgb_fit.yml \
rtheta_to_xy_fit.yml \
xy_to_rtheta_fit.yml \
kelv_to_uv.gen_c_fixed

install_srgb: install_common
	cp srgb_uv_to_rgb.gen_py ../python/uv_to_rgb.py
	chmod a+x ../python/uv_to_rgb.py
	cp srgb_uv_to_rgb.gen_c_fixed ../c_fixed/uv_to_rgb.c
	cp srgb_uv_to_rgb.gen_c_float ../c_float/uv_to_rgb.c
	cp srgb_rgb_to_uv.gen_py ../python/rgb_to_uv.py
	chmod a+x ../python/rgb_to_uv.py
	cp srgb_rgb_to_uv.gen_c_fixed ../c_fixed/rgb_to_uv.c
	cp srgb_rgb_to_uv.gen_c_float ../c_float/rgb_to_uv.c
	cp srgb_mired_to_rgb.gen_py ../python/mired_to_rgb.py
	chmod a+x ../python/mired_to_rgb.py
	cp srgb_mired_to_rgb.gen_c_float ../c_float/mired_to_rgb.c
	cp srgb_mired_to_rgb.gen_c_fixed ../c_fixed/mired_to_rgb.c
	cp kelv_to_uv.gen_c_fixed ../c_fixed/kelv_to_uv.c

install_display_p3: install_common
	cp display_p3_uv_to_rgb.gen_py ../python/uv_to_rgb.py
	chmod a+x ../python/uv_to_rgb.py
	cp display_p3_uv_to_rgb.gen_c_fixed ../c_fixed/uv_to_rgb.c
	cp display_p3_uv_to_rgb.gen_c_float ../c_float/uv_to_rgb.c
	cp display_p3_rgb_to_uv.gen_py ../python/rgb_to_uv.py
	chmod a+x ../python/rgb_to_uv.py
	cp display_p3_rgb_to_uv.gen_c_fixed ../c_fixed/rgb_to_uv.c
	cp display_p3_rgb_to_uv.gen_c_float ../c_float/rgb_to_uv.c
	cp display_p3_mired_to_rgb.gen_py ../python/mired_to_rgb.py
	chmod a+x ../python/mired_to_rgb.py
	cp display_p3_mired_to_rgb.gen_c_float ../c_float/mired_to_rgb.c
	cp display_p3_mired_to_rgb.gen_c_fixed ../c_fixed/mired_to_rgb.c

# for displays that use SRGB gamma curve
install_srgb_common: install_common
	cp srgb_gamma_decode.gen_py ../python/gamma_decode.py
	chmod a+x ../python/gamma_decode.py
	cp srgb_gamma_decode.gen_c_fixed ../c_fixed/gamma_decode.c
	cp srgb_gamma_decode.gen_c_float ../c_float/gamma_decode.c
	cp srgb_gamma_encode.gen_py ../python/gamma_encode.py
	chmod a+x ../python/gamma_encode.py
	cp srgb_gamma_encode.gen_c_fixed ../c_fixed/gamma_encode.c
	cp srgb_gamma_encode.gen_c_float ../c_float/gamma_encode.c
	
install_common: all
	rm -f \
../python/kelv_rgb_6504K.py \
../c_float/kelv_rgb_6504K.inc \
../c_fixed/kelv_rgb_6504K.inc
	cp rtheta_to_xy.gen_py ../python/rtheta_to_xy.py
	chmod a+x ../python/rtheta_to_xy.py
	cp xy_to_rtheta.gen_py ../python/xy_to_rtheta.py
	chmod a+x ../python/xy_to_rtheta.py
	cp kelv_to_uv.gen_c_fixed ../c_fixed/kelv_to_uv.c
