#encoding=utf-8

import config
import colorsys
import maplib
import sparqllib

lat = 61.8
lng = 9.45

themap = config.make_map_from_cli_args()

symbols = {'true' : themap.add_symbol('white', '#FFFF00', '#000000',
                                      title = 'Dried'),
           'false' : themap.add_symbol('black', '#000000', '#000000',
                                       title = 'Not dried'),
           'http://www.garshol.priv.no/2014/neg/borderline' :
           themap.add_symbol('gray', '#999999', '#000000')}

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
    tb:yeast-keeping ?y.

  ?y tb:yeast-dried ?yeast.
}'''
for (s, lat, lng, title, yeast) in sparqllib.query_for_rows(query):
    symbol = symbols[yeast]
    themap.add_marker(lat, lng, title, symbol)

themap.set_legend(True)
themap.render_to('yeast-drying-map')
