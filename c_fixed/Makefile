CFLAGS=-g -Wall

%.o: %.c
	${CC} ${CFLAGS} ${CPPFLAGS} -c $<

%_standalone.o: %.c
	${CC} ${CFLAGS} ${CPPFLAGS} -DSTANDALONE -o $@ -c $<

all: hsbk_to_rgb rgb_to_hsbk gamma_decode gamma_encode kelv_to_rgb kelv_to_uv mired_to_rgb inv_test
# hsbk_to_rgb hsv_to_rgb rgb_to_hsbk rgb_to_hsv gamma_decode gamma_encode kelv_to_rgb kelv_to_uv mired_to_rgb hue_kelv_test inv_test sat_test

hsbk_to_rgb: hsbk_to_rgb_standalone.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm

hsv_to_rgb: hsv_to_rgb.o hsbk_to_rgb.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm -lpng

rgb_to_hsbk: rgb_to_hsbk_standalone.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm

rgb_to_hsv: rgb_to_hsv.o rgb_to_hsbk.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm -lpng

gamma_decode: gamma_decode_standalone.o
	${CC} ${CFLAGS} -o $@ $^ -lm

gamma_encode: gamma_encode_standalone.o
	${CC} ${CFLAGS} -o $@ $^ -lm

kelv_to_rgb: kelv_to_rgb_standalone.o kelv_to_uv.o gamma_encode.o
	${CC} ${CFLAGS} -o $@ $^ -lm

kelv_to_uv: kelv_to_uv_standalone.o
	${CC} ${CFLAGS} -o $@ $^ -lm

mired_to_rgb: mired_to_rgb_standalone.o
	${CC} ${CFLAGS} -o $@ $^ -lm

hue_kelv_test: hue_kelv_test.o hsbk_to_rgb.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm -lpng

inv_test: inv_test.o hsbk_to_rgb.o rgb_to_hsbk.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm

sat_test: sat_test.o hsbk_to_rgb.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm -lpng

clean:
	rm -f hsbk_to_rgb hsv_to_rgb rgb_to_hsbk rgb_to_hsv gamma_decode gamma_encode kelv_to_rgb kelv_to_uv mired_to_rgb hue_kelv_test inv_test sat_test *.o
