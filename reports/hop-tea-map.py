# encoding=utf-8

import config
import maputils

LANG = config.get_language()
labels = {
    'en' : {
        'true' : 'Hop tea',
        'false' : 'No hop tea',
        'borderline' : 'Borderline',
    },
    'no' : {
        'true' : u'Humle-te',
        'false' : u'Ikke humle-te',
        'borderline' : u'Både og',
    }
}

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT DISTINCT ?s ?lat ?lng ?title ?yeast
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:process ?proc.

  ?proc neg:hop-tea ?yeast.
}'''
maputils.make_boolean_map(query, config.get_file() or 'hop-tea-map',
                          labels[LANG])
