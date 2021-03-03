#encoding=utf-8

import colorsys
import config
import maplib
import sparqllib

maplib.DEFAULT_STROKEWEIGHT = 1
themap = config.make_map_from_cli_args()

NEG = 'http://www.garshol.priv.no/2014/neg/'
symbol = themap.add_symbol('yellow', '#FFFF00', title = 'Own yeast')

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix eu: <http://www.garshol.priv.no/2017/eu/>
prefix r: <http://www.garshol.priv.no/2014/trad-beer/recipe/>

SELECT DISTINCT ?s ?lat ?lng ?title
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:yeast-type neg:own-yeast.
}'''

for (s, lat, lng, title) in sparqllib.query_for_rows(query):
    themap.add_marker(lat, lng, title, symbol)

themap.render_to('own-yeast-map')
