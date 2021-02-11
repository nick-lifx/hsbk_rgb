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
gamma_decode_rec2020.py \
gamma_encode_srgb.py \
gamma_encode_rec2020.py \
uv_to_rgb_srgb.py \
uv_to_rgb_display_p3.py \
uv_to_rgb_rec2020.py \
rgb_to_uv_srgb.py \
rgb_to_uv_display_p3.py \
rgb_to_uv_rec2020.py \
mired_to_rgb_srgb.py \
mired_to_rgb_display_p3.py \
mired_to_rgb_rec2020.py \
rtheta_to_xy.py \
xy_to_rtheta.py \
xy_to_r.py \
rgb_to_hsbk_srgb.py \
rgb_to_hsbk_display_p3.py \
rgb_to_hsbk_rec2020.py

gamma_decode_srgb.py: \
../prepare/gamma_decode_fit_srgb.yml \
gamma_decode_device.py.template
	../prepare/gamma_decode_gen_py.py $< srgb <gamma_decode_device.py.template >$@
	chmod a+x $@

gamma_decode_rec2020.py: \
../prepare/gamma_decode_fit_rec2020.yml \
gamma_decode_device.py.template
	../prepare/gamma_decode_gen_py.py $< rec2020 <gamma_decode_device.py.template >$@
	chmod a+x $@

gamma_encode_srgb.py: \
../prepare/gamma_encode_fit_srgb.yml \
gamma_encode_device.py.template
	../prepare/gamma_encode_gen_py.py $< srgb <gamma_encode_device.py.template >$@
	chmod a+x $@

gamma_encode_rec2020.py: \
../prepare/gamma_encode_fit_rec2020.yml \
gamma_encode_device.py.template
	../prepare/gamma_encode_gen_py.py $< rec2020 <gamma_encode_device.py.template >$@
	chmod a+x $@

uv_to_rgb_srgb.py: \
../monitor/srgb/model.yml \
uv_to_rgb_device.py.template
	../prepare/uv_to_rgb_gen_py.py $< srgb srgb <uv_to_rgb_device.py.template >$@
	chmod a+x $@

uv_to_rgb_display_p3.py: \
../monitor/display_p3/model.yml \
uv_to_rgb_device.py.template
	../prepare/uv_to_rgb_gen_py.py $< srgb display_p3 <uv_to_rgb_device.py.template >$@
	chmod a+x $@

uv_to_rgb_rec2020.py: \
../monitor/rec2020/model.yml \
uv_to_rgb_device.py.template
	../prepare/uv_to_rgb_gen_py.py $< rec2020 rec2020 <uv_to_rgb_device.py.template >$@
	chmod a+x $@

rgb_to_uv_srgb.py: \
../monitor/srgb/model.yml \
rgb_to_uv_device.py.template
	../prepare/rgb_to_uv_gen_py.py $< srgb srgb <rgb_to_uv_device.py.template >$@
	chmod a+x $@

rgb_to_uv_display_p3.py: \
../monitor/display_p3/model.yml \
rgb_to_uv_device.py.template
	../prepare/rgb_to_uv_gen_py.py $< srgb display_p3 <rgb_to_uv_device.py.template <rgb_to_uv_device.py.template >$@
	chmod a+x $@

rgb_to_uv_rec2020.py: \
../monitor/rec2020/model.yml \
rgb_to_uv_device.py.template
	../prepare/rgb_to_uv_gen_py.py $< rec2020 rec2020 <rgb_to_uv_device.py.template >$@
	chmod a+x $@

mired_to_rgb_srgb.py: \
../prepare/mired_to_rgb_fit_srgb.yml \
mired_to_rgb_device.py.template
	../prepare/mired_to_rgb_gen_py.py $< srgb <mired_to_rgb_device.py.template >$@
	chmod a+x $@

mired_to_rgb_display_p3.py: \
../prepare/mired_to_rgb_fit_display_p3.yml \
mired_to_rgb_device.py.template
	../prepare/mired_to_rgb_gen_py.py $< display_p3 <mired_to_rgb_device.py.template >$@
	chmod a+x $@

mired_to_rgb_rec2020.py: \
../prepare/mired_to_rgb_fit_rec2020.yml \
mired_to_rgb_device.py.template
	../prepare/mired_to_rgb_gen_py.py $< rec2020 <mired_to_rgb_device.py.template >$@
	chmod a+x $@

rtheta_to_xy.py: ../prepare/rtheta_to_xy_fit.yml rtheta_to_xy.py.template
	../prepare/rtheta_to_xy_gen_py.py $< <$@.template >$@
	chmod a+x $@

xy_to_rtheta.py: ../prepare/xy_to_rtheta_fit.yml xy_to_rtheta.py.template
	../prepare/xy_to_rtheta_gen_py.py $< <$@.template >$@
	chmod a+x $@

xy_to_r.py: ../prepare/xy_to_r_fit.yml xy_to_r.py.template
	../prepare/xy_to_r_gen_py.py $< <$@.template >$@
	chmod a+x $@

# most generator scripts live in ../prepare, but this one is special,
# as it needs to run the previously generated code in this directory
# (it must link to code for all monitors so list all as dependencies)
rgb_to_hsbk_srgb.py: \
mired_to_rgb_srgb.py \
mired_to_rgb_display_p3.py \
mired_to_rgb_rec2020.py
	./rgb_to_hsbk_gen.py srgb >$@
	chmod a+x $@

# most generator scripts live in ../prepare, but this one is special,
# as it needs to run the previously generated code in this directory
# (it must link to code for all monitors so list all as dependencies)
rgb_to_hsbk_display_p3.py: \
mired_to_rgb_srgb.py \
mired_to_rgb_display_p3.py \
mired_to_rgb_rec2020.py
	./rgb_to_hsbk_gen.py display_p3 >$@
	chmod a+x $@

# most generator scripts live in ../prepare, but this one is special,
# as it needs to run the previously generated code in this directory
# (it must link to code for all monitors so list all as dependencies)
rgb_to_hsbk_rec2020.py: \
mired_to_rgb_srgb.py \
mired_to_rgb_display_p3.py \
mired_to_rgb_rec2020.py
	./rgb_to_hsbk_gen.py rec2020 >$@
	chmod a+x $@

clean:
	rm -f \
gamma_decode_*.py \
gamma_encode_*.py \
uv_to_rgb_*.py \
rgb_to_uv_*.py \
mired_to_rgb_*.py \
rtheta_to_xy.py \
xy_to_rtheta.py \
xy_to_r.py \
rgb_to_hsbk_srgb.py \
rgb_to_hsbk_display_p3.py \
rgb_to_hsbk_rec2020.py
