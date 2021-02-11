#!/bin/sh

ext=.py
for i in python c_float c_fixed
do
  (
    ../$i/hsbk_to_rgb_srgb$ext 60 0 1 5000
    ../$i/hsbk_to_rgb_display_p3$ext 60 0 1 5000
    ../$i/hsbk_to_rgb_rec2020$ext 60 0 1 5000

    ../$i/rgb_to_hsbk_srgb$ext .5 .5 .5
    ../$i/rgb_to_hsbk_display_p3$ext .5 .5 .5
    ../$i/rgb_to_hsbk_rec2020$ext .5 .5 .5

    ../$i/rgb_to_hsbk_srgb$ext .5 .5 .5 5000
    ../$i/rgb_to_hsbk_display_p3$ext .5 .5 .5 5000
    ../$i/rgb_to_hsbk_rec2020$ext .5 .5 .5 5000

    ../$i/rgb_to_uv_srgb$ext .5 .5 .5
    ../$i/rgb_to_uv_display_p3$ext .5 .5 .5
    ../$i/rgb_to_uv_rec2020$ext .5 .5 .5

    ../$i/uv_to_rgb_srgb$ext .3 .3
    ../$i/uv_to_rgb_display_p3$ext .3 .3
    ../$i/uv_to_rgb_rec2020$ext .3 .3

    ../$i/kelv_to_uv$ext 5000
  ) >out_$i.txt

  ext=
done

# the following have not been ported to all directories yet:
../python/uv_to_kelv.py 0.211503 0.323009
../c_float/uv_to_kelv 0.211503 0.323009

../python/xy_to_r.py .5 .5
../python/xy_to_r.py .5 -.5
../python/xy_to_r.py -.5 .5
../python/xy_to_r.py -.5 -.5

../python/xy_to_rtheta.py .5 .5
../python/xy_to_rtheta.py .5 -.5
../python/xy_to_rtheta.py -.5 .5
../python/xy_to_rtheta.py -.5 -.5

../python/rtheta_to_xy.py 0.707107 0.785398
../python/rtheta_to_xy.py 0.707107 -0.785398
../python/rtheta_to_xy.py 0.707107 2.356194
../python/rtheta_to_xy.py 0.707107 -2.356194
