
#encoding=utf-8

import maputils

query = '''
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>

select ?s ?title ?treat ?lat ?lng where {
  ?s dc:title ?title;
    tb:process ?proc;
    geo:lat ?lat;
    geo:long ?lng.

  ?proc tb:hop-treatment ?treat.
}
'''

PREFIX = 'http://www.garshol.priv.no/2014/trad-beer/'
symbols = [
    (PREFIX + 'hop-tea',            '#00FF00', {
        'en' : 'Hop tea', 'no' : 'Humle-te',
    }),
    (PREFIX + 'boil-hops-in-wort',  '#FF0000', {
        'en' : 'Boil in wort', 'no' : u'Kokt i vørter'
    }),
    (PREFIX + 'humlebeit',          '#0000FF', 'Humlebeit'),
    (PREFIX + 'boil-hops-in-mash',  '#00FFFF', {
        'en' : 'Boil in mash', 'no' : 'Kokt i mesk'
    }),
    (PREFIX + 'hops-in-mash',       '#FFFF00', {
        'en' : 'Hops in mash', 'no' : 'Humle i mesk'
    }),
    (PREFIX + 'dry-hopping',        '#FFFFFF', {
        'en' : 'Dry-hopping', 'no' : u'Tørrhumling'
    }),
    (PREFIX + 'lauter-through-hops','#AAAAAA', {
        'en' : 'Lauter through hops', 'no' : 'Renn gjennom humle'
    }),
]
maputils.make_thing_map(query, symbols, 'hop-treatment-map', legend = True)
