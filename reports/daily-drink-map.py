
#encoding=utf-8

import re
import maputils

query = '''
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>

select ?s ?title ?drink ?lat ?lng where {
  ?s dc:title ?title;
    tb:daily-drink ?drink;
    geo:lat ?lat;
    geo:long ?lng.

}
'''

PREFIX = 'http://www.garshol.priv.no/2014/neg/'
symbols = [
    (PREFIX + 'small-beer',  '#00FF00', 'Small beer'),
    (PREFIX + 'blande',      '#FF0000', 'Blande'),
    (PREFIX + 'milk',        '#FFFFFF', 'Milk'),
    (PREFIX + 'sour-milk',   '#0000FF', 'Sour milk'),
]
maputils.make_thing_map(query, symbols, 'daily-drink-map', legend = True)
