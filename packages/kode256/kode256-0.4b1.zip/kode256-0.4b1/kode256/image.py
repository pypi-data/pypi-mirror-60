#! /usr/bin/env python3

# Copyright (c) 2014-2016 Felix Knopf <e01100101@t-online.de>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License in the LICENSE.txt for more details.
#
# This part of the library is based on code128.py by Erik Karulf,
# found at https://gist.github.com/ekarulf/701416
# His original copyright and permission notice:
#    Copyright (c) 2010 Erik Karulf <erik@karulf.com>
#  
#    Permission to use, copy, modify, and/or distribute this software for any
#    purpose with or without fee is hereby granted, provided that the above
#    copyright notice and this permission notice appear in all copies.
#

try: from PIL import Image, ImageDraw, ImageFont
except ImportError:
    try: import Image, ImageDraw, ImageFont
    except ImportError:
        Image = None
        
import os.path
from .format import code128_format as _format

def code128_image(data, height=100, thickness=3, caption=False, quiet_zone=True):
    """encodes 'data' in a code128 barcode and returns an Image object"""
    if Image is None:
        raise ImportError("PIL not found, only SVG output possible")

    barcode_widths = _format(data, thickness)
    width = sum(barcode_widths)
    x = 0

    font = ImageFont.truetype(os.path.join(os.path.dirname(__file__),
                                "Inconsolata-Regular.ttf"), height//6)
    text_dim    = font.getsize(data)
    h_ext       = caption*(height//20 +text_dim[1]) 

    if quiet_zone:
        width += 20 * thickness
        x = 10 * thickness

    # Monochrome Image
    img  = Image.new('L', (width, height+h_ext), 255)
    draw = ImageDraw.Draw(img)
    draw_bar = True
    for w in barcode_widths:
        if draw_bar:
            draw.rectangle(((x, 0), (x + w - 1, height)), fill=0)
        draw_bar = not draw_bar
        x += w

    if caption:        # draw human readable representation
        draw.text( ((width-text_dim[0])/2,round(height*41/40)), data, font=font)        

    return img

