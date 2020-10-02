all: kelv_to_rgb_srgb.gen_py mired_to_rgb_srgb.gen_py kelv_to_uv.gen_c_fixed

kelv_to_rgb_srgb.gen_py: UVW_to_rgb_srgb.yml
	./kelv_to_rgb_gen_py.py $^ >$@

mired_to_rgb_srgb.gen_py: mired_to_rgb_fit_srgb.yml
	./mired_to_rgb_gen_py.py $^ >$@

mired_to_rgb_fit_srgb.yml: mired_to_uv_data.yml UVW_to_rgb_srgb.yml
	./mired_to_rgb_fit.py $^ $@

mired_to_uv_data.yml:
	./mired_to_uv_data.py $@

UVW_to_rgb_srgb.yml: rgbw_to_xy_srgb.yml
	./UVW_to_rgb.py $^ $@

kelv_to_uv.gen_c_fixed:
	./kelv_to_uv_gen_c_fixed.py >$@

clean:
	rm -f kelv_to_rgb_srgb.gen_py mired_to_rgb_srgb.gen_py kelv_to_uv.gen_c_fixed mired_to_rgb_fit_srgb.yml mired_to_uv.yml UVW_to_rgb_srgb.yml

install: all
	cp kelv_to_rgb_srgb.gen_py ../python/kelv_to_rgb.py
	chmod a+x ../python/kelv_to_rgb.py
	cp mired_to_rgb_srgb.gen_py ../python/mired_to_rgb.py
	chmod a+x ../python/mired_to_rgb.py
	cp kelv_to_uv.gen_c_fixed ../c_fixed/kelv_to_uv.c
