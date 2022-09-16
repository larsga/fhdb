# encoding=utf-8

import config
import sparqllib

config.parser.add_argument('--recipe', action='store_true')
recipe = config._get_args().recipe

themap = config.make_map_from_cli_args()
LANG = config.get_language()

labels = {
'en' : {
    'used' : 'Hops used',
    'not'  : 'Not used',
    },
'no' : {
    'used' : 'Humle brukt',
    'not' :  'Ikke brukt',
    },
}[LANG]

white = themap.add_symbol('#FFFF00', '#000000', strokeweight = 1,
                          title = labels['used'])
black = themap.add_symbol('#000000', '#000000', strokeweight = 1,
                          title = labels['not'])

query = '''
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
SELECT ?s ?title ?lat ?lng ?herb
WHERE {
  ?s
    a ?klass;
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:%sherbs ?herb.

  FILTER( ?klass != tb:ArchaeologicalFind )
}''' % ('recipe-' if recipe else '')

result = list(sparqllib.query_for_rows(query))
accounts = { s : (title, lat, lng, False)
             for (s, title, lat, lng, herb) in result }

for (s, title, lat, lng, herbs) in result:
    if herbs.endswith('/hops'):
        (title, lat, lng, _) = accounts[s]
        accounts[s] = (title, lat, lng, True)

for (title, lat, lng, hops) in accounts.values():
    themap.add_marker(lat, lng, title, white if hops else black)

themap.set_legend(True)
themap.render_to(config.get_file() or 'hop-usage-map')
