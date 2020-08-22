
#encoding=utf-8

import re, codecs, sys
import maplib, mapniklib, sparqllib, mapgenlib, config
import pitch

# ===== ALL IN ONE DATA SET

themap = config.make_map_from_cli_args()

symbol_count = 10
smallest = 0
biggest = 40
increment = (biggest - smallest) / (symbol_count - 1)

if themap.get_color():
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
        themap.add_marker(lat, lng, '%s' % t, symbol)

themap.set_legend(True)
themap.render_to('pitch-temperature-map')
