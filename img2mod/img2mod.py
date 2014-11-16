#!/usr/bin/env python
#
# img2mod - A script to convert an image file into a PCB module file for Kicad.
# Version 1.01 - November 21, 2010
#
# Written by Matthew Beckler for Wayne and Layne, LLC
# Copyright (c) 2011, Wayne and Layne, LLC
# http://img2mod.wayneandlayne.com/ - wayneandlayne at wayneandlayne dot com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.


from PIL import Image

# Text for the file header, the parameter is the name of the module, ex "LOGO".
header = """PCBNEW-LibModule-V1
$INDEX
%(name)s
$EndINDEX
$MODULE %(name)s
Po 0 0 0 15 00000000 00000000 ~~
T0 0 2866 600 600 0 120 N I 21 "G***"
T1 0 -2866 600 600 0 120 N I 21 "%(name)s"
"""

# Text for the file footer, the only parameter is the name of the module
footer = """$EndMODULE %(name)s
$EndLIBRARY
"""

# Places a pixel with (x, y) at the upper-left corner
# Size is in units of 0.1 mil = 0.0001 inch
def make_pixel(x, y, px_size):
    return """DP 0 0 0 0 5 1 21
Dl %(0)s %(1)s
Dl %(2)s %(1)s
Dl %(2)s %(3)s
Dl %(0)s %(3)s
Dl %(0)s %(1)s
""" % {"0": x, "1": y, "2": x + px_size, "3": y + px_size}

def conv_image_to_module(image, module_name, scale_factor):
    """ Returns the text for the module, and the size: (x, y) in inches. """
    w, h = image.size
    #print "Original image dimensions: {0} x {1}".format(w, h)
    #print "Writing module file to \"{0}\"".format(output_filename)
    module = header % {"name": module_name}
    for y in range(h):
        for x in range(w):
            #print image.getpixel((x,y))
            if image.getpixel((x, y)) == 0:
                module += make_pixel(scale_factor * x, scale_factor * y, scale_factor)
    module += footer % {"name": module_name}
    return module, ((scale_factor * w) / 10000.0, (scale_factor * h) / 10000.0)


def main():
    import sys

    if len(sys.argv) < 5:
        print "Usage: %s input_image output_filename module_name scale_factor" % sys.argv[0]
        print "  input_image is the filename of the input image"
        print "  output_filename is the name of the output module file"
        print "  module_name is the name to use for the module, traditionally LOGO"
        print "  scale_factor is the size of each output pixel, in units of 0.1 mil = 0.0001\""
        sys.exit(1)

    input_image = sys.argv[1]
    output_filename = sys.argv[2]
    module_name = sys.argv[3]
    scale_factor = int(sys.argv[4])

    print "Reading image from \"%s\"" % input_image

    # If we .convert("1") it makes a binary image with a 127 threshold
    # Keeping it at greyscale allows us to make the threshold configurable
    image = Image.open(input_image).convert("L")
    # The above conversion will assume a black background for removing transparency.
    # If we want to use a different background color, use this:
    #white = Image.new("RGB", image.size, (255,255,255))
    #r,g,b,a = image.split()
    #image = Image.composite(image, white, a)

    # If you want to invert the image:
    # image = PIL.ImageOps.invert(image)

    # If you want to do non-127 thresholding, change the 127 below
    image = image.point(lambda i: 0 if i < 127 else 255)

    module, size = conv_image_to_module(image, module_name, scale_factor)
    print "Output image size: %f x %f inches" % (size[0], size[1])

    fid = open(output_filename, "w")
    fid.write(module)
    fid.close()

if __name__ == "__main__":
    main()

