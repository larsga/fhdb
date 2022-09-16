#encoding=utf-8

import colorsys
import config
import maplib
import sparqllib

maplib.DEFAULT_STROKEWEIGHT = 1
themap = config.make_map_from_cli_args()

NEG = 'http://www.garshol.priv.no/2014/neg/'
symbols = {
    NEG + 'own-yeast' : themap.add_symbol('#FFFF00',
                                          title = 'Own yeast'),
    NEG + 'bakers-yeast' : themap.add_symbol('#000000',
                                             title = "Baker's yeast"),
    NEG + 'brewers-yeast' : themap.add_symbol('#0000FF',
                                              title = "Brewer's yeast"),
    NEG + 'lager-yeast' : themap.add_symbol('#CCCCFF',
                                            title = 'Lager yeast'),
    NEG + 'distillers-yeast' : themap.add_symbol('#FF0000',
                                                 title = "Distiller's yeast"),
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

themap.set_legend(True)
themap.render_to('yeast-type-map')
