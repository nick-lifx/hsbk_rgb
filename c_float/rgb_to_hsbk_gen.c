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
        "device in {srgb, display_p3}\n",
      argv[0]
    );
    exit(EXIT_FAILURE);
  }
  const char *device = argv[1];

  float rgb[N_RGB];
  if (strcmp(device, "srgb") == 0)
    mired_to_rgb_srgb(1e6f / 6504.f, rgb);
  else if (strcmp(device, "display_p3") == 0)
    mired_to_rgb_display_p3(1e6f / 6504.f, rgb);
  else
    abort();

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
      "#include \"rgb_to_hsbk.h\"\n"
      "#include \"rgb_to_hsbk_%s.h\"\n"
      "\n"
      "#define RGB_RED 0\n"
      "#define RGB_GREEN 1\n"
      "#define RGB_BLUE 2\n"
      "#define N_RGB 3\n"
      "\n"
      "static float kelv_rgb_6504K[N_RGB] = {\n"
      "  %.8e,\n\n"
      "  %.8e,\n\n"
      "  %.8e\n\n"
      "};\n"
      "\n"
      "void rgb_to_hsbk_%s(const float *rgb, float kelv, float *hsbk) {\n"
      "  rgb_to_hsbk(kelv_rgb_6504K, mired_to_rgb_%s, rgb, kelv, hsbk);\n"
      "}\n"
      "\n"
      "#ifdef STANDALONE\n"
      "int rgb_to_hsbk_standalone(\n"
      "  void (*_rgb_to_hsbk)(const float *rgb, float kelv, float *hsbk),\n"
      "  int argc,\n"
      "  char **argv\n"
      ");\n"
      "\n"
      "int main(int argc, char **argv) {\n"
      "  return rgb_to_hsbk_standalone(rgb_to_hsbk_%s, argc, argv);\n"
      "}\n"
      "#endif\n",
    device,
    device,
    rgb[RGB_RED],
    rgb[RGB_GREEN],
    rgb[RGB_BLUE],
    device,
    device,
    device
  );
  return EXIT_SUCCESS;
}
