# encoding=utf-8

import config
import maputils

LANG = config.get_language()
labels = {
    'en' : {
        'true' : 'Juniper infusion',
        'false' : 'No infusion',
        'borderline' : 'Borderline',
    },
    'no' : {
        'true' : u'Einerlåg',
        'false' : u'Ikke einerlåg',
        'borderline' : u'Både og',
    }
}

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT DISTINCT ?s ?lat ?lng ?title ?mead
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:juniper-infusion ?mead.
}'''
maputils.make_boolean_map(query, config.get_file() or 'juniper-infusion-map',
                          labels[LANG])
