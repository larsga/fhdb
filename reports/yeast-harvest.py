#encoding=utf-8

import maplib
import sparqllib
import config

lat = 61.8
lng = 9.45

themap = config.make_map_from_cli_args()

NEG = 'http://www.garshol.priv.no/2014/neg/'

BLACK = themap.add_symbol('black', '#000000', '#000000', title = 'Bottom')
DARK_GRAY = themap.add_symbol('dark_gray', '#555555', '#000000',
                              title = 'Cask bottom')
EITHER = themap.add_symbol('gray', '#999999', '#000000', title = 'Either')

symbols =  {
    NEG + 'top' : themap.add_symbol('white', '#FFFFFF', '#000000',
                                    title = 'Top'),
    NEG + 'bottom' : BLACK,
    NEG + 'cask-bottom' : DARK_GRAY,
    NEG + 'either' : EITHER,
    NEG + 'both' : EITHER
}

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix eu: <http://www.garshol.priv.no/2017/eu/>
prefix r: <http://www.garshol.priv.no/2014/trad-beer/recipe/>

SELECT DISTINCT ?s ?lat ?lng ?title ?harvest
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:yeast-harvest ?harvest.
}'''
for (s, lat, lng, title, harvest) in sparqllib.query_for_rows(query):
    try:
        symbol = symbols[harvest]
    except KeyError:
        print 'KeyError:', s, harvest
        raise
    themap.add_marker(lat, lng, title, symbol)

themap.set_legend(True)
themap.render_to('yeast-harvest')
