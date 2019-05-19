'''
Utilities for generating specific kinds of maps.
'''

import colorsys
import maplib
import sparqllib
import math

def chex(color):
    return hex(int(color * 255))[2 : ].zfill(2)

def rgb(hue, saturation, vrightness):
    (r, g, b) = colorsys.hsv_to_rgb(hue, saturation, vrightness)
    return chex(r) + chex(g) + chex(b)

def color(value, symbols):
    import colormaps
    # ratio = math.log(value + 1) / math.log(symbols)
    # return chex(ratio) + chex(ratio) + chex(ratio)
    (r, g, b) = colormaps._magma_data[value]
    return chex(r) + chex(g) + chex(b)

# these are essentially parameters
zoom = 6
center_lat = 61.8
center_lng = 9.45
symbol_count = 256
max_scale = 25

def value_mapper(v):
    'Remap values for better visualization.'
    return math.log(v)

def color_scale_map(query, outfile, max_value = 1000000):
    themap = maplib.Map(center_lat, center_lng, zoom)

    symbols = [themap.add_symbol('id%s' % ix,
                                 '#' + color(ix, symbol_count),
                                 '#000000',
                                 strokeweight = 1#,
                                 #scale = (ix / float(symbol_count)) * max_scale
               )
               for ix in range(symbol_count)]

    smallest = 1000000
    biggest = 0
    for (lat, lng, title, ratio) in sparqllib.query_for_rows(query):
        value = value_mapper(min(float(ratio), max_value))
        smallest = min(smallest, value)
        biggest = max(biggest, value)

    increment = (biggest - smallest) / (symbol_count - 1)
    for (lat, lng, title, org_value) in sparqllib.query_for_rows(query):
        ratio = value_mapper(min(float(org_value), max_value))
        index = (int((ratio - smallest) / increment))
        symbol = symbols[index]
        themap.add_marker(lat, lng, title, symbol, 'Value: %s' % org_value)

    themap.render_to(outfile)
