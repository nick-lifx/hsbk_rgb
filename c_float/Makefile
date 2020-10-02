CFLAGS=-g -Wall

%.o: %.c
	${CC} ${CFLAGS} ${CPPFLAGS} -c $<

%_standalone.o: %.c
	${CC} ${CFLAGS} ${CPPFLAGS} -DSTANDALONE -o $@ -c $<

all: hsbk_to_rgb rgb_to_hsbk kelv_to_rgb kelv_to_uv mired_to_rgb inv_test

hsbk_to_rgb: hsbk_to_rgb_standalone.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm

rgb_to_hsbk: rgb_to_hsbk_standalone.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^

kelv_to_rgb: kelv_to_rgb_standalone.o kelv_to_uv.o
	${CC} ${CFLAGS} -o $@ $^ -lm

kelv_to_uv: kelv_to_uv_standalone.o
	${CC} ${CFLAGS} -o $@ $^

mired_to_rgb: mired_to_rgb_standalone.o
	${CC} ${CFLAGS} -o $@ $^

inv_test: inv_test.o hsbk_to_rgb.o rgb_to_hsbk.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm

clean:
	rm -f hsbk_to_rgb rgb_to_hsbk kelv_to_rgb kelv_to_uv mired_to_rgb inv_test *.o
