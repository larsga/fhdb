
import colorsys
import maplib
import sparqllib

lat = 61.8
lng = 9.45

themap = maplib.Map(lat, lng, 6)

symbols = {
    '1' : themap.add_symbol('white', '#FFFFFF', '#000000'),
    '0' : themap.add_symbol('black', '#000000', '#000000'),
    'true' : themap.add_symbol('white', '#FFFFFF', '#000000'),
    'false' : themap.add_symbol('black', '#000000', '#000000')
}

query = '''
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
    tb:mead ?mead.
}'''
count = 0
for (s, lat, lng, title, mead) in sparqllib.query_for_rows(query):
    symbol = symbols[mead]
    themap.add_marker(lat, lng, title, symbol)
    count += 1

themap.render_to('mead.html')
