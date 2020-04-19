#encoding=utf-8

import colorsys
import config
import maplib
import sparqllib

themap = config.make_map_from_cli_args()

symbols = {'true' : themap.add_symbol('white', '#FFFF00', '#000000'),
           'false' : themap.add_symbol('black', '#000000', '#000000'),
           'http://www.garshol.priv.no/2014/neg/borderline' :
           themap.add_symbol('gray', '#999999', '#000000', strokeweight = 1)}

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
    tb:own-yeast ?yeast.

  FILTER( ?yeast )
}'''

  # FILTER( ?yeast )
  # ?s tb:year ?y.
  # FILTER( ?y >= 2000 )
  # OPTIONAL { ?s eu:author ?auth }
  # FILTER( ?auth != "Per Persson" )
  # FILTER( ?title != "Muhu museum director")
  # FILTER( ?s not in (r:r172) )

for (s, lat, lng, title, yeast) in sparqllib.query_for_rows(query):
    symbol = symbols[yeast]
    themap.add_marker(lat, lng, title, symbol)

themap.render_to('own-yeast.html')
