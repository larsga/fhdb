# encoding=utf-8

import config
import maplib
import sparqllib

themap = config.make_map_from_cli_args()
LANG = config.get_language()

labels = {
'en' : {
    'none' : 'No alder',
    'filter' : 'Filter only'
    },
'no' : {
    'none' : 'Ingen or',
    'filter' : 'Bare i rost'
    },
}[LANG]

white = themap.add_symbol('white', '#FFFFFF', '#000000', strokeweight = 1,
                          title = labels['filter'])
black = themap.add_symbol('black', '#000000', '#000000', strokeweight = 1,
                          title = labels['none'])

ALDER = 'http://www.garshol.priv.no/2014/neg/alder-branches'
query = '''
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
SELECT ?s ?title ?lat ?lng ?filter
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:strainer ?filter.
}'''
accounts = {}
for (s, title, lat, lng, what) in sparqllib.query_for_rows(query):
    accounts[s] = (s, title, lat, lng, what == ALDER or accounts.get(s, (None, None, None, None, False))[-1])

for (s, title, lat, lng, alder) in accounts.values():
    themap.add_marker(lat, lng, title, white if alder else black)

themap.set_legend(True)
themap.render_to(config.get_file() or 'alder-map')
