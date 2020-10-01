mired_to_rgb_srgb.py: mired_to_rgb_fit_srgb.yml
	./mired_to_rgb_to_py.py $^ $@
	chmod a+x $@

mired_to_rgb_fit_srgb.yml: mired_to_uv_data.yml rgbw_to_xy_srgb.yml
	./mired_to_rgb_fit.py $^ $@

mired_to_uv_data.yml:
	./mired_to_uv_data.py $@

clean:
	rm -f mired_to_rgb_srgb.py mired_to_rgb_fit_srgb.yml mired_to_uv_data.yml
