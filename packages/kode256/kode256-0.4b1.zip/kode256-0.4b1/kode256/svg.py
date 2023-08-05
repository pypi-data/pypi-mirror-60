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

from .format import code128_format as _format

def code128_svg(data, height=100, thickness=3, caption=False, quiet_zone=True):
    """encodes 'data' in a code128 barcode and returns an SVG graphic as string"""

    barcode_widths = _format(data, thickness)
    width = sum(barcode_widths)
    x = 0

    if quiet_zone:
        width += 20 * thickness
        x = 10 * thickness
        
    h_ext = caption*(height//40 + height//7)

    svg_elements = [ '<?xml version="1.0" encoding="UTF-8"?>\n'
                     '<svg width="%dpx" height="%dpx" xmlns="http://www.w3.org/2000/svg">' % \
                     (width, height+h_ext),
                     '    <rect width="%d" height="%d" fill="white"/>' % (width, height) ]
    draw_bar = True
    for w in barcode_widths:
        if draw_bar:
            svg_elements.append('    <rect x="%d" width="%d" height="%d"/>' % \
                                (x, w, height) )
        draw_bar = not draw_bar
        x += w

    if caption:
        svg_elements.append('   <text x="%d" y="%d" text-anchor="middle" font-size="%dpx" font-family="monospace">%s</text>' % \
                                     (width//2, height+h_ext, height//7,data) )
    svg_elements.append('</svg>')

    return "\n".join(svg_elements)
