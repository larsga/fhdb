# encoding=utf-8

import config
import maputils

LANG = config.get_language()
labels = {
    'en' : {
        'true' : 'Cold mash',
        'false' : 'No cold mash',
        'borderline' : 'Borderline',
    },
    'no' : {
        'true' : u'Kaldmesk',
        'false' : u'Ikke kaldmesk',
        'borderline' : u'Både og',
    }
}

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT DISTINCT ?s ?lat ?lng ?title ?yeast
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:process ?proc.

  ?proc tb:cold-mash ?yeast.
}'''
maputils.make_boolean_map(query, config.get_file() or 'cold-mash-map',
                          labels[LANG])
