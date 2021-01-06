#!/bin/sh

echo "python"

../python/hsbk_to_rgb_srgb.py 60 0 1 5000
../python/hsbk_to_rgb_display_p3.py 60 0 1 5000
../python/hsbk_to_rgb_rec2020.py 60 0 1 5000

../python/rgb_to_hsbk_srgb.py .5 .5 .5
../python/rgb_to_hsbk_display_p3.py .5 .5 .5
../python/rgb_to_hsbk_rec2020.py .5 .5 .5

../python/rgb_to_hsbk_srgb.py .5 .5 .5 5000
../python/rgb_to_hsbk_display_p3.py .5 .5 .5 5000
../python/rgb_to_hsbk_rec2020.py .5 .5 .5 5000

echo "c_float"

../c_float/hsbk_to_rgb_srgb 60 0 1 5000
../c_float/hsbk_to_rgb_display_p3 60 0 1 5000
../c_float/hsbk_to_rgb_rec2020 60 0 1 5000

../c_float/rgb_to_hsbk_srgb .5 .5 .5
../c_float/rgb_to_hsbk_display_p3 .5 .5 .5
../c_float/rgb_to_hsbk_rec2020 .5 .5 .5

../c_float/rgb_to_hsbk_srgb .5 .5 .5 5000
../c_float/rgb_to_hsbk_display_p3 .5 .5 .5 5000
../c_float/rgb_to_hsbk_rec2020 .5 .5 .5 5000

echo "c_fixed"

../c_fixed/hsbk_to_rgb_srgb 60 0 1 5000
../c_fixed/hsbk_to_rgb_display_p3 60 0 1 5000
../c_fixed/hsbk_to_rgb_rec2020 60 0 1 5000

../c_fixed/rgb_to_hsbk_srgb .5 .5 .5
../c_fixed/rgb_to_hsbk_display_p3 .5 .5 .5
../c_fixed/rgb_to_hsbk_rec2020 .5 .5 .5

../c_fixed/rgb_to_hsbk_srgb .5 .5 .5 5000
../c_fixed/rgb_to_hsbk_display_p3 .5 .5 .5 5000
../c_fixed/rgb_to_hsbk_rec2020 .5 .5 .5 5000
