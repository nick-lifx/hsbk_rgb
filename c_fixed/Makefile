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
hsbk_to_rgb \
hsv_to_rgb \
rgb_to_hsbk \
rgb_to_hsv \
gamma_decode \
gamma_encode \
uv_to_rgb \
rgb_to_uv \
kelv_to_uv \
mired_to_rgb \
hue_kelv_test \
inv_test \
sat_test \
gamma_decode_srgb.c \
gamma_encode_srgb.c \
uv_to_rgb_srgb.c \
rgb_to_uv_srgb.c \
mired_to_rgb_srgb.c \
uv_to_rgb_display_p3.c \
rgb_to_uv_display_p3.c \
mired_to_rgb_display_p3.c \
kelv_to_uv.gen_c_fixed

hsbk_to_rgb: hsbk_to_rgb_standalone.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm

hsv_to_rgb: hsv_to_rgb.o hsbk_to_rgb.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm -lpng

rgb_to_hsbk: rgb_to_hsbk_standalone.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm

rgb_to_hsbk_standalone.o: rgb_to_hsbk.c kelv_rgb_6504K.inc

kelv_rgb_6504K.inc: kelv_rgb_6504K_gen
	./kelv_rgb_6504K_gen >$@

kelv_rgb_6504K_gen: kelv_rgb_6504K_gen.o hsbk_to_rgb.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm -lpng

rgb_to_hsv: rgb_to_hsv.o rgb_to_hsbk.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm -lpng

gamma_decode: gamma_decode_standalone.o
	${CC} ${CFLAGS} -o $@ $^ -lm

gamma_encode: gamma_encode_standalone.o
	${CC} ${CFLAGS} -o $@ $^ -lm

uv_to_rgb: uv_to_rgb_standalone.o gamma_encode.o
	${CC} ${CFLAGS} -o $@ $^ -lm

rgb_to_uv: rgb_to_uv_standalone.o gamma_decode.o
	${CC} ${CFLAGS} -o $@ $^ -lm

kelv_to_uv: kelv_to_uv_standalone.o
	${CC} ${CFLAGS} -o $@ $^ -lm

mired_to_rgb: mired_to_rgb_standalone.o
	${CC} ${CFLAGS} -o $@ $^ -lm

hue_kelv_test: hue_kelv_test.o hsbk_to_rgb.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm -lpng

inv_test: inv_test.o hsbk_to_rgb.o rgb_to_hsbk.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm

sat_test: sat_test.o hsbk_to_rgb.o mired_to_rgb.o rgb_to_uv.o gamma_decode.o
	${CC} ${CFLAGS} -o $@ $^ -lm -lpng

gamma_decode_srgb.c: ../prepare/gamma_decode_fit_srgb.yml
	../prepare/gamma_decode_gen_c_fixed.py $^ >$@

gamma_encode_srgb.c: ../prepare/gamma_encode_fit_srgb.yml
	../prepare/gamma_encode_gen_c_fixed.py $^ >$@

uv_to_rgb_srgb.c: ../prepare/primaries_srgb.yml
	../prepare/uv_to_rgb_gen_c_fixed.py $^ >$@

rgb_to_uv_srgb.c: ../prepare/primaries_srgb.yml
	../prepare/rgb_to_uv_gen_c_fixed.py $^ >$@

mired_to_rgb_srgb.c: ../prepare/mired_to_rgb_fit_srgb.yml
	../prepare/mired_to_rgb_gen_c_fixed.py $^ >$@

uv_to_rgb_display_p3.c: ../prepare/primaries_display_p3.yml
	../prepare/uv_to_rgb_gen_c_fixed.py $^ >$@

rgb_to_uv_display_p3.c: ../prepare/primaries_display_p3.yml
	../prepare/rgb_to_uv_gen_c_fixed.py $^ >$@

mired_to_rgb_display_p3.c: ../prepare/mired_to_rgb_fit_display_p3.yml
	../prepare/mired_to_rgb_gen_c_fixed.py $^ >$@

kelv_to_uv.gen_c_fixed:
	../prepare/kelv_to_uv_gen_c_fixed.py >$@

clean:
	rm -f \
hsbk_to_rgb \
hsv_to_rgb \
rgb_to_hsbk \
kelv_rgb_6504K.inc \
kelv_rgb_6504K_gen \
rgb_to_hsv \
gamma_decode \
gamma_encode \
uv_to_rgb \
rgb_to_uv \
kelv_to_uv \
mired_to_rgb \
hue_kelv_test \
inv_test \
sat_test \
gamma_decode_srgb.c \
gamma_encode_srgb.c \
uv_to_rgb_srgb.c \
rgb_to_uv_srgb.c \
mired_to_rgb_srgb.c \
uv_to_rgb_display_p3.c \
rgb_to_uv_display_p3.c \
mired_to_rgb_display_p3.c \
kelv_to_uv.gen_c_fixed \
*.o
