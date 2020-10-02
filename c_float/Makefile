CFLAGS=-g -Wall

%.o: %.c
	${CC} ${CFLAGS} ${CPPFLAGS} -c $<

%_standalone.o: %.c
	${CC} ${CFLAGS} ${CPPFLAGS} -DSTANDALONE -o $@ -c $<

all: hsbk_to_rgb rgb_to_hsbk mired_to_rgb

hsbk_to_rgb: hsbk_to_rgb_standalone.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^ -lm

rgb_to_hsbk: rgb_to_hsbk_standalone.o mired_to_rgb.o
	${CC} ${CFLAGS} -o $@ $^

mired_to_rgb: mired_to_rgb_standalone.o
	${CC} ${CFLAGS} -o $@ $^

clean:
	rm -f hsbk_to_rgb rgb_to_hsbk mired_to_rgb *.o
