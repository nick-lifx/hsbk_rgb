all: gamma_decode_srgb.gen_py gamma_decode_srgb.gen_c_float gamma_decode_srgb.gen_c_fixed gamma_encode_srgb.gen_py gamma_encode_srgb.gen_c_float gamma_encode_srgb.gen_c_fixed kelv_to_rgb_srgb.gen_py kelv_to_rgb_srgb.gen_c_fixed kelv_to_rgb_srgb.gen_c_float mired_to_rgb_srgb.gen_py mired_to_rgb_srgb.gen_c_float kelv_to_uv.gen_c_fixed

gamma_decode_srgb.gen_py: gamma_decode_fit_srgb.yml
	./gamma_decode_gen_py.py $^ >$@

gamma_decode_srgb.gen_c_fixed: gamma_decode_fit_srgb.yml
	./gamma_decode_gen_c_fixed.py $^ >$@

gamma_decode_srgb.gen_c_float: gamma_decode_fit_srgb.yml
	./gamma_decode_gen_c_float.py $^ >$@

gamma_decode_fit_srgb.yml:
	./gamma_decode_fit.py $^ $@

gamma_encode_srgb.gen_py: gamma_encode_fit_srgb.yml
	./gamma_encode_gen_py.py $^ >$@

gamma_encode_srgb.gen_c_fixed: gamma_encode_fit_srgb.yml
	./gamma_encode_gen_c_fixed.py $^ >$@

gamma_encode_srgb.gen_c_float: gamma_encode_fit_srgb.yml
	./gamma_encode_gen_c_float.py $^ >$@

gamma_encode_fit_srgb.yml:
	./gamma_encode_fit.py $^ $@

kelv_to_rgb_srgb.gen_py: UVW_to_rgb_srgb.yml
	./kelv_to_rgb_gen_py.py $^ >$@

kelv_to_rgb_srgb.gen_c_fixed: UVW_to_rgb_srgb.yml
	./kelv_to_rgb_gen_c_fixed.py $^ >$@

kelv_to_rgb_srgb.gen_c_float: UVW_to_rgb_srgb.yml
	./kelv_to_rgb_gen_c_float.py $^ >$@

UVW_to_rgb_srgb.yml: rgbw_to_xy_srgb.yml
	./UVW_to_rgb.py $^ $@

mired_to_rgb_srgb.gen_py: mired_to_rgb_fit_srgb.yml
	./mired_to_rgb_gen_py.py $^ >$@

mired_to_rgb_srgb.gen_c_float: mired_to_rgb_fit_srgb.yml
	./mired_to_rgb_gen_c_float.py $^ >$@

mired_to_rgb_fit_srgb.yml: mired_to_uv_data.yml UVW_to_rgb_srgb.yml
	./mired_to_rgb_fit.py $^ $@

mired_to_uv_data.yml:
	./mired_to_uv_data.py $@

kelv_to_uv.gen_c_fixed:
	./kelv_to_uv_gen_c_fixed.py >$@

clean:
	rm -f gamma_decode_srgb.gen_py gamma_decode_srgb.gen_c_fixed gamma_decode_srgb.gen_c_float gamma_decode_fit_srgb.yml gamma_encode_srgb.gen_py gamma_encode_srgb.gen_c_fixed gamma_encode_srgb.gen_c_float gamma_encode_fit_srgb.yml kelv_to_rgb_srgb.gen_py kelv_to_rgb_srgb.gen_c_fixed kelv_to_rgb_srgb.gen_c_float UVW_to_rgb_srgb.yml mired_to_rgb_srgb.gen_py mired_to_rgb_srgb.gen_c_float kelv_to_uv.gen_c_fixed mired_to_rgb_fit_srgb.yml mired_to_uv.yml

install: all
	cp gamma_decode_srgb.gen_py ../python/gamma_decode.py
	chmod a+x ../python/gamma_decode.py
	cp gamma_decode_srgb.gen_c_fixed ../c_fixed/gamma_decode.c
	cp gamma_decode_srgb.gen_c_float ../c_float/gamma_decode.c
	cp gamma_encode_srgb.gen_py ../python/gamma_encode.py
	chmod a+x ../python/gamma_encode.py
	cp gamma_encode_srgb.gen_c_fixed ../c_fixed/gamma_encode.c
	cp gamma_encode_srgb.gen_c_float ../c_float/gamma_encode.c
	cp kelv_to_rgb_srgb.gen_py ../python/kelv_to_rgb.py
	chmod a+x ../python/kelv_to_rgb.py
	cp kelv_to_rgb_srgb.gen_c_fixed ../c_fixed/kelv_to_rgb.c
	cp kelv_to_rgb_srgb.gen_c_float ../c_float/kelv_to_rgb.c
	cp mired_to_rgb_srgb.gen_py ../python/mired_to_rgb.py
	chmod a+x ../python/mired_to_rgb.py
	cp mired_to_rgb_srgb.gen_c_float ../c_float/mired_to_rgb.c
	cp kelv_to_uv.gen_c_fixed ../c_fixed/kelv_to_uv.c
