all: srgb_gamma_decode.gen_py srgb_gamma_decode.gen_c_float srgb_gamma_decode.gen_c_fixed srgb_gamma_encode.gen_py srgb_gamma_encode.gen_c_float srgb_gamma_encode.gen_c_fixed srgb_kelv_to_rgb.gen_py srgb_kelv_to_rgb.gen_c_fixed srgb_kelv_to_rgb.gen_c_float srgb_mired_to_rgb.gen_py srgb_mired_to_rgb.gen_c_float srgb_mired_to_rgb.gen_c_fixed display_p3_kelv_to_rgb.gen_py display_p3_kelv_to_rgb.gen_c_fixed display_p3_kelv_to_rgb.gen_c_float display_p3_mired_to_rgb.gen_py display_p3_mired_to_rgb.gen_c_float display_p3_mired_to_rgb.gen_c_fixed kelv_to_uv.gen_c_fixed

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

srgb_kelv_to_rgb.gen_py: srgb_primaries.yml
	./kelv_to_rgb_gen_py.py $^ >$@

srgb_kelv_to_rgb.gen_c_fixed: srgb_primaries.yml
	./kelv_to_rgb_gen_c_fixed.py $^ >$@

srgb_kelv_to_rgb.gen_c_float: srgb_primaries.yml
	./kelv_to_rgb_gen_c_float.py $^ >$@

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

display_p3_kelv_to_rgb.gen_py: display_p3_primaries.yml
	./kelv_to_rgb_gen_py.py $^ >$@

display_p3_kelv_to_rgb.gen_c_fixed: display_p3_primaries.yml
	./kelv_to_rgb_gen_c_fixed.py $^ >$@

display_p3_kelv_to_rgb.gen_c_float: display_p3_primaries.yml
	./kelv_to_rgb_gen_c_float.py $^ >$@

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

kelv_to_uv.gen_c_fixed:
	./kelv_to_uv_gen_c_fixed.py >$@

clean:
	rm -f srgb_gamma_decode.gen_py srgb_gamma_decode.gen_c_fixed srgb_gamma_decode.gen_c_float srgb_gamma_decode_fit.yml srgb_gamma_encode.gen_py srgb_gamma_encode.gen_c_fixed srgb_gamma_encode.gen_c_float srgb_gamma_encode_fit.yml srgb_kelv_to_rgb.gen_py srgb_kelv_to_rgb.gen_c_fixed srgb_kelv_to_rgb.gen_c_float srgb_primaries.yml srgb_mired_to_rgb.gen_py srgb_mired_to_rgb.gen_c_float srgb_mired_to_rgb.gen_c_fixed srgb_mired_to_rgb_fit.yml display_p3_kelv_to_rgb.gen_c_float display_p3_primaries.yml display_p3_mired_to_rgb.gen_py display_p3_mired_to_rgb.gen_c_float display_p3_mired_to_rgb.gen_c_fixed display_p3_mired_to_rgb_fit.yml kelv_to_uv.gen_c_fixed

install_srgb: all
	cp srgb_gamma_decode.gen_py ../python/gamma_decode.py
	chmod a+x ../python/gamma_decode.py
	cp srgb_gamma_decode.gen_c_fixed ../c_fixed/gamma_decode.c
	cp srgb_gamma_decode.gen_c_float ../c_float/gamma_decode.c
	cp srgb_gamma_encode.gen_py ../python/gamma_encode.py
	chmod a+x ../python/gamma_encode.py
	cp srgb_gamma_encode.gen_c_fixed ../c_fixed/gamma_encode.c
	cp srgb_gamma_encode.gen_c_float ../c_float/gamma_encode.c
	cp srgb_kelv_to_rgb.gen_py ../python/kelv_to_rgb.py
	chmod a+x ../python/kelv_to_rgb.py
	cp srgb_kelv_to_rgb.gen_c_fixed ../c_fixed/kelv_to_rgb.c
	cp srgb_kelv_to_rgb.gen_c_float ../c_float/kelv_to_rgb.c
	cp srgb_mired_to_rgb.gen_py ../python/mired_to_rgb.py
	chmod a+x ../python/mired_to_rgb.py
	cp srgb_mired_to_rgb.gen_c_float ../c_float/mired_to_rgb.c
	cp srgb_mired_to_rgb.gen_c_fixed ../c_fixed/mired_to_rgb.c
	cp kelv_to_uv.gen_c_fixed ../c_fixed/kelv_to_uv.c

install_display_p3: all
	cp srgb_gamma_decode.gen_py ../python/gamma_decode.py
	chmod a+x ../python/gamma_decode.py
	cp srgb_gamma_decode.gen_c_fixed ../c_fixed/gamma_decode.c
	cp srgb_gamma_decode.gen_c_float ../c_float/gamma_decode.c
	cp srgb_gamma_encode.gen_py ../python/gamma_encode.py
	chmod a+x ../python/gamma_encode.py
	cp srgb_gamma_encode.gen_c_fixed ../c_fixed/gamma_encode.c
	cp srgb_gamma_encode.gen_c_float ../c_float/gamma_encode.c
	cp display_p3_kelv_to_rgb.gen_py ../python/kelv_to_rgb.py
	chmod a+x ../python/kelv_to_rgb.py
	cp display_p3_kelv_to_rgb.gen_c_fixed ../c_fixed/kelv_to_rgb.c
	cp display_p3_kelv_to_rgb.gen_c_float ../c_float/kelv_to_rgb.c
	cp display_p3_mired_to_rgb.gen_py ../python/mired_to_rgb.py
	chmod a+x ../python/mired_to_rgb.py
	cp display_p3_mired_to_rgb.gen_c_float ../c_float/mired_to_rgb.c
	cp display_p3_mired_to_rgb.gen_c_fixed ../c_fixed/mired_to_rgb.c
	cp kelv_to_uv.gen_c_fixed ../c_fixed/kelv_to_uv.c
