
#encoding=utf-8

import re, codecs, sys
import maplib, mapniklib, sparqllib, mapgenlib
import pitch

# ===== ALL IN ONE DATA SET

color = True

themap = mapniklib.MapnikMap(mapniklib.make_simple_map(
        east = -4, west = 28, south = 52.5, north = 63.5,
        width = 2000, height = 1600,
        color = color
))

symbol_count = 10
smallest = 0
biggest = 40
increment = (biggest - smallest) / (symbol_count - 1)

if color:
    colorfunc = mapgenlib.color
else:
    colorfunc = mapgenlib.bwcolor

symbols = [themap.add_symbol('id%s' % ix,
                             '#' + colorfunc(ix, symbol_count),
                             '#000000',
                             strokeweight = 1,
                             scale = 10,
                             title = '%s-%sC' % (smallest + increment*ix, smallest + increment*(ix+1))
           )
           for ix in range(symbol_count)]

for (s, lat, lng, t, c) in sparqllib.query_for_rows(pitch.query):
    temp = pitch.get_temp(t)
    if temp:
        index = (int((temp - smallest) / increment))
        symbol = symbols[min(index, symbol_count - 1)]
        print temp, min(index, symbol_count - 1), symbol.get_color()
        themap.add_marker(lat, lng, 'No title', symbol)

themap.set_legend(True)
themap.render_to('pitch-temperature-map')
