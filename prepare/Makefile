all: srgb_gamma_decode.gen_py srgb_gamma_decode.gen_c_float srgb_gamma_decode.gen_c_fixed srgb_gamma_encode.gen_py srgb_gamma_encode.gen_c_float srgb_gamma_encode.gen_c_fixed srgb_kelv_to_rgb.gen_py srgb_kelv_to_rgb.gen_c_fixed srgb_kelv_to_rgb.gen_c_float srgb_mired_to_rgb.gen_py srgb_mired_to_rgb.gen_c_float srgb_mired_to_rgb.gen_c_fixed kelv_to_uv.gen_c_fixed

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

srgb_kelv_to_rgb.gen_py: srgb_UVW_to_rgb.yml
	./kelv_to_rgb_gen_py.py $^ >$@

srgb_kelv_to_rgb.gen_c_fixed: srgb_UVW_to_rgb.yml
	./kelv_to_rgb_gen_c_fixed.py $^ >$@

srgb_kelv_to_rgb.gen_c_float: srgb_UVW_to_rgb.yml
	./kelv_to_rgb_gen_c_float.py $^ >$@

srgb_UVW_to_rgb.yml: srgb_rgbw_to_xy.yml
	./UVW_to_rgb.py $^ $@

srgb_mired_to_rgb.gen_py: srgb_mired_to_rgb_fit.yml
	./mired_to_rgb_gen_py.py $^ >$@

srgb_mired_to_rgb.gen_c_float: srgb_mired_to_rgb_fit.yml
	./mired_to_rgb_gen_c_float.py $^ >$@

srgb_mired_to_rgb.gen_c_fixed: srgb_mired_to_rgb_fit.yml
	./mired_to_rgb_gen_c_fixed.py $^ >$@

srgb_mired_to_rgb_fit.yml: srgb_rgbw_to_xy.yml
	./mired_to_rgb_fit.py $^ $@

kelv_to_uv.gen_c_fixed:
	./kelv_to_uv_gen_c_fixed.py >$@

clean:
	rm -f srgb_gamma_decode.gen_py srgb_gamma_decode.gen_c_fixed srgb_gamma_decode.gen_c_float srgb_gamma_decode_fit.yml srgb_gamma_encode.gen_py srgb_gamma_encode.gen_c_fixed srgb_gamma_encode.gen_c_float srgb_gamma_encode_fit.yml srgb_kelv_to_rgb.gen_py srgb_kelv_to_rgb.gen_c_fixed srgb_kelv_to_rgb.gen_c_float srgb_UVW_to_rgb.yml srgb_mired_to_rgb.gen_py srgb_mired_to_rgb.gen_c_float srgb_mired_to_rgb.gen_c_fixed kelv_to_uv.gen_c_fixed srgb_mired_to_rgb_fit.yml

install: all
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
