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
gamma_decode_srgb.py \
gamma_encode_srgb.py \
uv_to_rgb_srgb.py \
uv_to_rgb_display_p3.py \
rgb_to_uv_srgb.py \
rgb_to_uv_display_p3.py \
mired_to_rgb_srgb.py \
mired_to_rgb_display_p3.py \
rtheta_to_xy.py \
xy_to_rtheta.py \
rgb_to_hsbk_srgb.py \
rgb_to_hsbk_display_p3.py

gamma_decode_srgb.py: ../prepare/gamma_decode_fit_srgb.yml
	../prepare/gamma_decode_gen_py.py $^ srgb >$@
	chmod a+x $@

gamma_encode_srgb.py: ../prepare/gamma_encode_fit_srgb.yml
	../prepare/gamma_encode_gen_py.py $^ srgb >$@
	chmod a+x $@

uv_to_rgb_srgb.py: ../prepare/primaries_srgb.yml
	../prepare/uv_to_rgb_gen_py.py $^ srgb srgb >$@
	chmod a+x $@

uv_to_rgb_display_p3.py: ../prepare/primaries_display_p3.yml
	../prepare/uv_to_rgb_gen_py.py $^ srgb display_p3 >$@
	chmod a+x $@

rgb_to_uv_srgb.py: ../prepare/primaries_srgb.yml
	../prepare/rgb_to_uv_gen_py.py $^ srgb srgb >$@
	chmod a+x $@

rgb_to_uv_display_p3.py: ../prepare/primaries_display_p3.yml
	../prepare/rgb_to_uv_gen_py.py $^ srgb display_p3 >$@
	chmod a+x $@

mired_to_rgb_srgb.py: ../prepare/mired_to_rgb_fit_srgb.yml
	../prepare/mired_to_rgb_gen_py.py $^ srgb >$@
	chmod a+x $@

mired_to_rgb_display_p3.py: ../prepare/mired_to_rgb_fit_display_p3.yml
	../prepare/mired_to_rgb_gen_py.py $^ display_p3 >$@
	chmod a+x $@

rtheta_to_xy.py: ../prepare/rtheta_to_xy_fit.yml
	../prepare/rtheta_to_xy_gen_py.py $^ >$@
	chmod a+x $@

xy_to_rtheta.py: ../prepare/xy_to_rtheta_fit.yml
	../prepare/xy_to_rtheta_gen_py.py $^ >$@
	chmod a+x $@

# most generator scripts live in ../prepare, but this one is special,
# as it needs to run the previously generated code in this directory
# (it must link to both srgb and display_p3 so list both dependencies)
rgb_to_hsbk_srgb.py: mired_to_rgb_srgb.py mired_to_rgb_display_p3.py
	./rgb_to_hsbk_gen.py srgb >$@
	chmod a+x $@

# most generator scripts live in ../prepare, but this one is special,
# as it needs to run the previously generated code in this directory
# (it must link to both srgb and display_p3 so list both dependencies)
rgb_to_hsbk_display_p3.py: mired_to_rgb_srgb.py mired_to_rgb_display_p3.py
	./rgb_to_hsbk_gen.py display_p3 >$@
	chmod a+x $@

clean:
	rm -f \
gamma_decode_srgb.py \
gamma_encode_srgb.py \
uv_to_rgb_srgb.py \
rgb_to_uv_srgb.py \
mired_to_rgb_srgb.py \
uv_to_rgb_display_p3.py \
rgb_to_uv_display_p3.py \
mired_to_rgb_display_p3.py \
rtheta_to_xy.py \
xy_to_rtheta.py \
rgb_to_hsbk_srgb.py \
rgb_to_hsbk_display_p3.py
