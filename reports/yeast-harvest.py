#encoding=utf-8

import colorsys
import maplib
import sparqllib

lat = 61.8
lng = 9.45

themap = maplib.GoogleMap(lat, lng, 6)

NEG = 'http://www.garshol.priv.no/2014/neg/'
BLACK = themap.add_symbol('black', '#000000', '#000000')
DARK_GRAY = themap.add_symbol('dark_gray', '#555555', '#000000')
symbols =  {
    NEG + 'top' : themap.add_symbol('white', '#FFFFFF', '#000000'),
    NEG + 'bottom' : BLACK,
    NEG + 'cask-bottom' : DARK_GRAY,
    NEG + 'either' : themap.add_symbol('gray', '#999999', '#000000'),
    NEG + 'both' : themap.add_symbol('gray', '#999999', '#000000')
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

themap.render_to('yeast-harvest.html')
