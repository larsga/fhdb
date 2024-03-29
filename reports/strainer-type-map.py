
# encoding=utf-8

import re, sys
import maputils

mapview = sys.argv[1] if len(sys.argv) > 1 else None

query = '''
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>

select ?s ?title ?strainer ?lat ?lng where {
  ?s dc:title ?title;
    tb:strainer-type ?strainer;
    geo:lat ?lat;
    geo:long ?lng.
}
'''

PREFIX = 'http://www.garshol.priv.no/2018/trad-beer/strainer/'
symbols = [
    (PREFIX + 'S',  '#00FF00', 'S'),
    (PREFIX + 'B',  '#0000FF', 'B'),
    (PREFIX + 'SB',  '#00FFFF', 'SB')
] + ([
    (PREFIX + 'K',  '#FF0000', 'K'),
    (PREFIX + 'KA', '#FFFF00', 'KA'),
    (PREFIX + 'KB', '#FF00FF', 'KB'),
] if (mapview not in ('norway-montage')) else [])
maputils.make_thing_map(query, symbols, 'strainer-type-map', legend = True)
