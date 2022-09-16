
#encoding=utf-8

import re, codecs, sys
import maplib, mapniklib, sparqllib, maputils, config
import pitch

data = []
for (s, lat, lng, t, c) in sparqllib.query_for_rows(pitch.query):
    temp = pitch.get_temp(t)
    if temp:
        data.append((lat, lng, '', temp))

maputils.color_scale_map_data(data, 'pitch-temperature-map', True)
