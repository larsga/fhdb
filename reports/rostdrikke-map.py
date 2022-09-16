# encoding=utf-8

import maputils, config

maputils.make_boolean_map('''
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
    tb:rostdrikke ?mead.
}''',
filename = config.get_file() or 'rostdrikke-map',
labels = {
    'en' : {
        'true' : 'Rostdrikke made',
        'false' : 'No rostdrikke',
        'borderline' : 'Borderline',
    },
    'no' : {
        'true' : 'Rostdrikke laget',
        'false' : 'Ingen rostdrikke',
        'borderline' : 'Gråsone',
    },
}[config.get_language()])
