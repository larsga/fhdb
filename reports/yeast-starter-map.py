
# encoding=utf-8

import config
import maputils

LANG = config.get_language()
labels = {
    'en' : {
        'true' : 'Yeast starter',
        'false' : 'No starter',
        'borderline' : 'Borderline',
    },
    'no' : {
        'true' : u'Gjærstarter',
        'false' : u'Ingen starter',
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
    tb:yeast-starter ?yeast.
}'''
maputils.make_boolean_map(query, config.get_file() or 'yeast-starter-map',
                          labels[LANG])
