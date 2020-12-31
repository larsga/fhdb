
# encoding=utf-8

import maputils

query = '''
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>

select ?s ?title ?cat ?lat ?lng where {
  ?s dc:title ?title;
    tb:oppskake2 ?cat;
    geo:lat ?lat;
    geo:long ?lng.

}
'''

PREFIX = 'http://www.garshol.priv.no/2014/neg/'
symbols = [
    (PREFIX + 'party',         '#FFFF00', u'Oppskåke'),
    (PREFIX + 'house-party',   '#FFFFFF', 'House party'),
    (PREFIX + 'house-tasting', '#AAAAAA', 'House tasting'),
    (PREFIX + 'skokubolle',    '#00FF00', 'Skokubolle'),
    (PREFIX + 'none',          '#000000', 'Nothing'),
]
maputils.make_thing_map(query, symbols, 'oppskake-map', legend = True)
