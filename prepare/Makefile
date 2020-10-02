all: kelv_to_rgb_srgb.py mired_to_rgb_srgb.py

kelv_to_rgb_srgb.py: UVW_to_rgb_srgb.yml
	./kelv_to_rgb_gen.py $^ $@
	chmod a+x $@

mired_to_rgb_srgb.py: mired_to_rgb_fit_srgb.yml
	./mired_to_rgb_gen.py $^ $@
	chmod a+x $@

mired_to_rgb_fit_srgb.yml: mired_to_uv_data.yml UVW_to_rgb_srgb.yml
	./mired_to_rgb_fit.py $^ $@

mired_to_uv_data.yml:
	./mired_to_uv_data.py $@

UVW_to_rgb_srgb.yml: rgbw_to_xy_srgb.yml
	./UVW_to_rgb.py $^ $@

clean:
	rm -f kelv_to_rgb_srgb.py mired_to_rgb_srgb.py mired_to_rgb_fit_srgb.yml mired_to_uv.yml UVW_to_rgb_srgb.yml

install:
	cp kelv_to_rgb_srgb.py mired_to_rgb_srgb.py ..
