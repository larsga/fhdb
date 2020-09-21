#encoding=utf-8

import colorsys
import config
import maplib
import sparqllib

themap = config.make_map_from_cli_args()

NEG = 'http://www.garshol.priv.no/2014/neg/'
symbols = {
    NEG + 'own-yeast' : themap.add_symbol('yellow', '#FFFF00', strokeweight = 1),
    NEG + 'bakers-yeast' : themap.add_symbol('black', '#000000', strokeweight = 1),
    NEG + 'brewers-yeast' : themap.add_symbol('blue', '#0000FF', strokeweight = 1),
    NEG + 'lager-yeast' : themap.add_symbol('paleblue', '#CCCCFF', strokeweight = 1),
    NEG + 'distillers-yeast' : themap.add_symbol('red', '#FF0000', strokeweight = 1),
}

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix eu: <http://www.garshol.priv.no/2017/eu/>
prefix r: <http://www.garshol.priv.no/2014/trad-beer/recipe/>

SELECT DISTINCT ?s ?lat ?lng ?title ?yeast
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:yeast-type ?yeast.

}'''

for (s, lat, lng, title, yeast) in sparqllib.query_for_rows(query):
    symbol = symbols[yeast]
    themap.add_marker(lat, lng, title, symbol)

themap.render_to('yeast-type-map')
