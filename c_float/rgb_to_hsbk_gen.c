// Copyright (c) 2020 Nick Downing
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to
// deal in the Software without restriction, including without limitation the
// rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
// sell copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
// IN THE SOFTWARE.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "mired_to_rgb_display_p3.h"
#include "mired_to_rgb_rec2020.h"
#include "mired_to_rgb_srgb.h"

#define EXIT_SUCCESS 0
#define EXIT_FAILURE 1

#define RGB_RED 0
#define RGB_GREEN 1
#define RGB_BLUE 2
#define N_RGB 3

// precompute RGB for 6504K, used for rgb_to_hsbk with kelv == 0.f
// most generator scripts live in ../prepare, but this one is special,
// as it needs to run the previously generated code in this directory

int main(int argc, char **argv) {
  if (argc < 2) {
    printf(
      "usage: %s device\n"
        "device in {srgb, display_p3, rec2020}\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }
  const char *device = argv[1];

  const struct mired_to_rgb *mired_to_rgb;
  if (strcmp(device, "srgb") == 0)
    mired_to_rgb = &mired_to_rgb_srgb;
  else if (strcmp(device, "display_p3") == 0)
    mired_to_rgb = &mired_to_rgb_display_p3;
  else if (strcmp(device, "rec2020") == 0)
    mired_to_rgb = &mired_to_rgb_rec2020;
  else
    abort();

  float rgb[N_RGB];
  mired_to_rgb_convert(mired_to_rgb, 1e6f / 6504.f, rgb);

  printf(
    "// Copyright (c) 2020 Nick Downing\n"
      "//\n"
      "// Permission is hereby granted, free of charge, to any person obtaining a copy\n"
      "// of this software and associated documentation files (the \"Software\"), to\n"
      "// deal in the Software without restriction, including without limitation the\n"
      "// rights to use, copy, modify, merge, publish, distribute, sublicense, and/or\n"
      "// sell copies of the Software, and to permit persons to whom the Software is\n"
      "// furnished to do so, subject to the following conditions:\n"
      "//\n"
      "// The above copyright notice and this permission notice shall be included in\n"
      "// all copies or substantial portions of the Software.\n"
      "//\n"
      "// THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n"
      "// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
      "// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
      "// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
      "// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING\n"
      "// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS\n"
      "// IN THE SOFTWARE.\n"
      "\n"
      "#include \"mired_to_rgb_%s.h\"\n"
      "#include \"rgb_to_hsbk_%s.h\"\n"
      "\n"
      "const struct rgb_to_hsbk rgb_to_hsbk_%s = {\n"
      "  {%.8ef, %.8ef, %.8ef},\n"
      "  &mired_to_rgb_%s\n"
      "};\n"
      "\n"
      "#ifdef STANDALONE\n"
      "int rgb_to_hsbk_standalone(\n"
      "  const struct rgb_to_hsbk *rgb_to_hsbk,\n"
      "  int argc,\n"
      "  char **argv\n"
      ");\n"
      "\n"
      "int main(int argc, char **argv) {\n"
      "  return rgb_to_hsbk_standalone(&rgb_to_hsbk_%s, argc, argv);\n"
      "}\n"
      "#endif\n",
    device,
    device,
    device,
    rgb[RGB_RED],
    rgb[RGB_GREEN],
    rgb[RGB_BLUE],
    device,
    device
  );
  return EXIT_SUCCESS;
}
