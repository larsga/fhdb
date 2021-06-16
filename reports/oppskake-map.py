
# encoding=utf-8

import config
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

labels = {
    'en' : {
        'party' :         u'Oppskåke',
        'house-tasting' : 'House tasting',
        'skokubolle' :    'Skokubolle',
        'none' :          'Nothing',
    },
    'no' : {
        'party' :         u'Oppskåke',
        'house-tasting' : 'Husstanden smaker',
        'skokubolle' :    'Skokubolle',
        'none' :          'Ingen markering',
    }
}

LANG = config.get_language()
PREFIX = 'http://www.garshol.priv.no/2014/neg/'
symbols = [
    (PREFIX + 'party',         '#FFFF00', labels[LANG]['party']),
    (PREFIX + 'house-tasting', '#AAAAAA', labels[LANG]['house-tasting']),
    (PREFIX + 'skokubolle',    '#00FF00', labels[LANG]['skokubolle']),
    (PREFIX + 'none',          '#000000', labels[LANG]['none']),
]
maputils.make_thing_map(query, symbols,
                        config.get_file() or 'oppskake-map',
                        legend = True)
