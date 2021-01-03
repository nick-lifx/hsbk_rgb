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

CFLAGS=-g -Wall

%.o: %.c
	${CC} ${CFLAGS} ${CPPFLAGS} -c $<

%_standalone.o: %.c
	${CC} ${CFLAGS} ${CPPFLAGS} -DSTANDALONE -o $@ -c $<

all: \
hsbk_to_rgb_srgb \
hsbk_to_rgb_display_p3 \
hsbk_to_rgb_rec2020 \
rgb_to_hsbk_srgb \
rgb_to_hsbk_display_p3 \
rgb_to_hsbk_rec2020 \
gamma_decode_srgb \
gamma_decode_rec2020 \
gamma_encode_srgb \
gamma_encode_rec2020 \
uv_to_rgb_srgb \
uv_to_rgb_display_p3 \
uv_to_rgb_rec2020 \
rgb_to_uv_srgb \
rgb_to_uv_display_p3 \
rgb_to_uv_rec2020 \
mired_to_rgb_srgb \
mired_to_rgb_display_p3 \
mired_to_rgb_rec2020 \
kelv_to_uv \
kelv_to_uv_deriv \
uv_to_kelv \
hsv_to_rgb \
rgb_to_hsv \
hue_kelv_test \
inv_test \
sat_test

hsbk_to_rgb_srgb: \
hsbk_to_rgb_srgb_standalone.o \
hsbk_to_rgb_standalone.o \
mired_to_rgb.o \
mired_to_rgb_srgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm

hsbk_to_rgb_display_p3: \
hsbk_to_rgb_display_p3_standalone.o \
hsbk_to_rgb_standalone.o \
mired_to_rgb.o \
mired_to_rgb_display_p3.o
	${CC} ${CFLAGS} -o $@ $^ -lm

hsbk_to_rgb_rec2020: \
hsbk_to_rgb_rec2020_standalone.o \
hsbk_to_rgb_standalone.o \
mired_to_rgb.o \
mired_to_rgb_rec2020.o
	${CC} ${CFLAGS} -o $@ $^ -lm

rgb_to_hsbk_srgb: \
rgb_to_hsbk_srgb_standalone.o \
rgb_to_hsbk_standalone.o \
mired_to_rgb.o \
mired_to_rgb_srgb.o
	${CC} ${CFLAGS} -o $@ $^

rgb_to_hsbk_srgb.c: rgb_to_hsbk_gen
	./rgb_to_hsbk_gen srgb >$@

rgb_to_hsbk_display_p3: \
rgb_to_hsbk_display_p3_standalone.o \
rgb_to_hsbk_standalone.o \
mired_to_rgb.o \
mired_to_rgb_display_p3.o
	${CC} ${CFLAGS} -o $@ $^

rgb_to_hsbk_display_p3.c: rgb_to_hsbk_gen
	./rgb_to_hsbk_gen display_p3 >$@

rgb_to_hsbk_rec2020: \
rgb_to_hsbk_rec2020_standalone.o \
rgb_to_hsbk_standalone.o \
mired_to_rgb.o \
mired_to_rgb_rec2020.o
	${CC} ${CFLAGS} -o $@ $^

rgb_to_hsbk_rec2020.c: rgb_to_hsbk_gen
	./rgb_to_hsbk_gen rec2020 >$@

gamma_decode_srgb: gamma_decode_srgb_standalone.o
	${CC} ${CFLAGS} -o $@ $^

gamma_decode_srgb.c: ../prepare/gamma_decode_fit_srgb.yml
	../prepare/gamma_decode_gen_c_float.py $^ srgb >$@

gamma_decode_rec2020: gamma_decode_rec2020_standalone.o
	${CC} ${CFLAGS} -o $@ $^

gamma_decode_rec2020.c: ../prepare/gamma_decode_fit_rec2020.yml
	../prepare/gamma_decode_gen_c_float.py $^ rec2020 >$@

gamma_encode_srgb: gamma_encode_srgb_standalone.o
	${CC} ${CFLAGS} -o $@ $^

gamma_encode_srgb.c: ../prepare/gamma_encode_fit_srgb.yml
	../prepare/gamma_encode_gen_c_float.py $^ srgb >$@

gamma_encode_rec2020: gamma_encode_rec2020_standalone.o
	${CC} ${CFLAGS} -o $@ $^

gamma_encode_rec2020.c: ../prepare/gamma_encode_fit_rec2020.yml
	../prepare/gamma_encode_gen_c_float.py $^ rec2020 >$@

uv_to_rgb_srgb: uv_to_rgb_srgb_standalone.o gamma_encode_srgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm

uv_to_rgb_srgb.c: ../monitor/srgb/model.yml
	../prepare/uv_to_rgb_gen_c_float.py $^ srgb srgb >$@

uv_to_rgb_display_p3: uv_to_rgb_display_p3_standalone.o gamma_encode_srgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm

uv_to_rgb_display_p3.c: ../monitor/display_p3/model.yml
	../prepare/uv_to_rgb_gen_c_float.py $^ srgb display_p3 >$@

uv_to_rgb_rec2020: uv_to_rgb_rec2020_standalone.o gamma_encode_rec2020.o
	${CC} ${CFLAGS} -o $@ $^ -lm

uv_to_rgb_rec2020.c: ../monitor/rec2020/model.yml
	../prepare/uv_to_rgb_gen_c_float.py $^ rec2020 rec2020 >$@

rgb_to_uv_srgb: rgb_to_uv_srgb_standalone.o gamma_decode_srgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm

rgb_to_uv_srgb.c: ../monitor/srgb/model.yml
	../prepare/rgb_to_uv_gen_c_float.py $^ srgb srgb  >$@

rgb_to_uv_display_p3: rgb_to_uv_display_p3_standalone.o gamma_decode_srgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm

rgb_to_uv_display_p3.c: ../monitor/display_p3/model.yml
	../prepare/rgb_to_uv_gen_c_float.py $^ srgb display_p3 >$@

rgb_to_uv_rec2020: rgb_to_uv_rec2020_standalone.o gamma_decode_rec2020.o
	${CC} ${CFLAGS} -o $@ $^ -lm

rgb_to_uv_rec2020.c: ../monitor/rec2020/model.yml
	../prepare/rgb_to_uv_gen_c_float.py $^ rec2020 rec2020  >$@

mired_to_rgb_srgb: \
mired_to_rgb_standalone.o \
mired_to_rgb_srgb_standalone.o
	${CC} ${CFLAGS} -o $@ $^

mired_to_rgb_srgb.c: ../prepare/mired_to_rgb_fit_srgb.yml
	../prepare/mired_to_rgb_gen_c_float.py $^ srgb >$@

mired_to_rgb_display_p3: \
mired_to_rgb_standalone.o \
mired_to_rgb_display_p3_standalone.o
	${CC} ${CFLAGS} -o $@ $^

mired_to_rgb_display_p3.c: ../prepare/mired_to_rgb_fit_display_p3.yml
	../prepare/mired_to_rgb_gen_c_float.py $^ display_p3 >$@

mired_to_rgb_rec2020: \
mired_to_rgb_standalone.o \
mired_to_rgb_rec2020_standalone.o
	${CC} ${CFLAGS} -o $@ $^

mired_to_rgb_rec2020.c: ../prepare/mired_to_rgb_fit_rec2020.yml
	../prepare/mired_to_rgb_gen_c_float.py $^ rec2020 >$@

kelv_to_uv: kelv_to_uv_standalone.o
	${CC} ${CFLAGS} -o $@ $^

kelv_to_uv_deriv: kelv_to_uv_deriv_standalone.o
	${CC} ${CFLAGS} -o $@ $^

uv_to_kelv: uv_to_kelv_standalone.o kelv_to_uv_deriv.o
	${CC} ${CFLAGS} -o $@ $^ -lm

hsv_to_rgb: \
hsv_to_rgb.o \
hsbk_to_rgb_srgb.o \
hsbk_to_rgb_display_p3.o \
hsbk_to_rgb_rec2020.o \
hsbk_to_rgb.o \
mired_to_rgb.o \
mired_to_rgb_srgb.o \
mired_to_rgb_display_p3.o \
mired_to_rgb_rec2020.o
	${CC} ${CFLAGS} -o $@ $^ -lm -lpng

rgb_to_hsv: \
rgb_to_hsv.o \
rgb_to_hsbk_srgb.o \
rgb_to_hsbk_display_p3.o \
rgb_to_hsbk_rec2020.o \
rgb_to_hsbk.o \
mired_to_rgb.o \
mired_to_rgb_srgb.o \
mired_to_rgb_display_p3.o \
mired_to_rgb_rec2020.o
	${CC} ${CFLAGS} -o $@ $^ -lm -lpng

hue_kelv_test: \
hue_kelv_test.o \
hsbk_to_rgb_srgb.o \
hsbk_to_rgb_display_p3.o \
hsbk_to_rgb_rec2020.o \
hsbk_to_rgb.o \
mired_to_rgb.o \
mired_to_rgb_srgb.o \
mired_to_rgb_display_p3.o \
mired_to_rgb_rec2020.o
	${CC} ${CFLAGS} -o $@ $^ -lm -lpng

inv_test: \
inv_test.o \
hsbk_to_rgb_srgb.o \
hsbk_to_rgb_display_p3.o \
hsbk_to_rgb_rec2020.o \
hsbk_to_rgb.o \
rgb_to_hsbk_srgb.o \
rgb_to_hsbk_display_p3.o \
rgb_to_hsbk_rec2020.o \
rgb_to_hsbk.o \
mired_to_rgb.o \
mired_to_rgb_srgb.o \
mired_to_rgb_display_p3.o \
mired_to_rgb_rec2020.o
	${CC} ${CFLAGS} -o $@ $^ -lm

sat_test: \
sat_test.o \
hsbk_to_rgb_srgb.o \
hsbk_to_rgb_display_p3.o \
hsbk_to_rgb_rec2020.o \
hsbk_to_rgb.o \
mired_to_rgb.o \
mired_to_rgb_srgb.o \
mired_to_rgb_display_p3.o \
mired_to_rgb_rec2020.o \
rgb_to_uv_srgb.o \
rgb_to_uv_display_p3.o \
rgb_to_uv_rec2020.o \
gamma_decode_srgb.o \
gamma_decode_rec2020.o
	${CC} ${CFLAGS} -o $@ $^ -lm -lpng

# most generator scripts live in ../prepare, but this one is special,
# as it needs to run the previously generated code in this directory
# (it must link to both srgb and display_p3 so list both dependencies)
rgb_to_hsbk_gen: \
rgb_to_hsbk_gen.o \
mired_to_rgb.o \
mired_to_rgb_srgb.o \
mired_to_rgb_display_p3.o \
mired_to_rgb_rec2020.o
	${CC} ${CFLAGS} -o $@ $^ -lm

clean:
	rm -f \
hsbk_to_rgb_srgb \
hsbk_to_rgb_display_p3 \
hsbk_to_rgb_rec2020 \
rgb_to_hsbk_srgb \
rgb_to_hsbk_srgb.c \
rgb_to_hsbk_display_p3 \
rgb_to_hsbk_display_p3.c \
rgb_to_hsbk_rec2020 \
rgb_to_hsbk_rec2020.c \
gamma_decode_srgb \
gamma_decode_srgb.c \
gamma_decode_rec2020 \
gamma_decode_rec2020.c \
gamma_encode_srgb \
gamma_encode_srgb.c \
gamma_encode_rec2020 \
gamma_encode_rec2020.c \
uv_to_rgb_srgb \
uv_to_rgb_srgb.c \
uv_to_rgb_display_p3 \
uv_to_rgb_display_p3.c \
uv_to_rgb_rec2020 \
uv_to_rgb_rec2020.c \
rgb_to_uv_srgb \
rgb_to_uv_srgb.c \
rgb_to_uv_display_p3 \
rgb_to_uv_display_p3.c \
rgb_to_uv_rec2020 \
rgb_to_uv_rec2020.c \
mired_to_rgb_srgb \
mired_to_rgb_srgb.c \
mired_to_rgb_display_p3 \
mired_to_rgb_display_p3.c \
mired_to_rgb_rec2020 \
mired_to_rgb_rec2020.c \
kelv_to_uv \
kelv_to_uv_deriv \
uv_to_kelv \
hsv_to_rgb \
rgb_to_hsv \
hue_kelv_test \
inv_test \
sat_test \
rgb_to_hsbk_gen \
*.o
