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
gamma_decode_fit_srgb.yml \
gamma_decode_fit_rec2020.yml \
gamma_encode_fit_srgb.yml \
gamma_encode_fit_rec2020.yml \
mired_to_rgb_fit_srgb.yml \
mired_to_rgb_fit_display_p3.yml \
mired_to_rgb_fit_rec2020.yml \
rtheta_to_xy_fit.yml \
xy_to_rtheta_fit.yml \
xy_to_r_fit.yml

gamma_decode_fit_srgb.yml: ../monitor/srgb/model.yml
	./gamma_decode_fit.py $^ $@

gamma_decode_fit_rec2020.yml: ../monitor/rec2020/model.yml
	./gamma_decode_fit.py $^ $@

gamma_encode_fit_srgb.yml: ../monitor/srgb/model.yml
	./gamma_encode_fit.py $^ $@

gamma_encode_fit_rec2020.yml: ../monitor/rec2020/model.yml
	./gamma_encode_fit.py $^ $@

mired_to_rgb_fit_srgb.yml: ../monitor/srgb/model.yml
	./mired_to_rgb_fit.py $^ 150 500 $@

mired_to_rgb_fit_display_p3.yml: ../monitor/display_p3/model.yml
	./mired_to_rgb_fit.py $^ 150 950 $@

mired_to_rgb_fit_rec2020.yml: ../monitor/rec2020/model.yml
	./mired_to_rgb_fit.py $^ 150 950 $@

rtheta_to_xy_fit.yml:
	./rtheta_to_xy_fit.py $@

xy_to_rtheta_fit.yml:
	./xy_to_rtheta_fit.py $@

xy_to_r_fit.yml:
	./xy_to_r_fit.py $@

clean:
	rm -f \
gamma_decode_fit_*.yml \
gamma_encode_fit_*.yml \
mired_to_rgb_fit_*.yml \
rtheta_to_xy_fit.yml \
xy_to_rtheta_fit.yml \
xy_to_r_fit.yml
