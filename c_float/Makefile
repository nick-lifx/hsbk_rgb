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
kelv_to_rgb \
kelv_to_uv \
mired_to_rgb \
hue_kelv_test \
inv_test \
sat_test

hsbk_to_rgb: hsbk_to_rgb_standalone.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm

hsv_to_rgb: hsv_to_rgb.o hsbk_to_rgb.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm -lpng

rgb_to_hsbk: rgb_to_hsbk_standalone.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^

rgb_to_hsv: rgb_to_hsv.o rgb_to_hsbk.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm -lpng

gamma_decode: gamma_decode_standalone.o
	${CC} ${CFLAGS} -o $@ $^

gamma_encode: gamma_encode_standalone.o
	${CC} ${CFLAGS} -o $@ $^

kelv_to_rgb: kelv_to_rgb_standalone.o kelv_to_uv.o gamma_encode.o
	${CC} ${CFLAGS} -o $@ $^ -lm

kelv_to_uv: kelv_to_uv_standalone.o
	${CC} ${CFLAGS} -o $@ $^

mired_to_rgb: mired_to_rgb_standalone.o
	${CC} ${CFLAGS} -o $@ $^

hue_kelv_test: hue_kelv_test.o hsbk_to_rgb.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm -lpng

inv_test: inv_test.o hsbk_to_rgb.o rgb_to_hsbk.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm

sat_test: sat_test.o hsbk_to_rgb.o mired_to_rgb.o gamma_decode.o
	${CC} ${CFLAGS} -o $@ $^ -lm -lpng

clean:
	rm -f \
hsbk_to_rgb \
hsv_to_rgb \
rgb_to_hsbk \
rgb_to_hsv \
gamma_decode \
gamma_encode \
kelv_to_rgb \
kelv_to_uv \
mired_to_rgb \
hue_kelv_test \
inv_test \
sat_test \
*.o
