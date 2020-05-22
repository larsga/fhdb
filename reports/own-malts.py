
import colorsys
import config
import sparqllib

themap = config.make_map_from_cli_args()

symbols = {'true' : themap.add_symbol('white', '#FFFFFF', '#000000'),
           'false' : themap.add_symbol('black', '#000000', '#000000'),
           'http://www.garshol.priv.no/2014/neg/both' :
           themap.add_symbol('gray', '#999999', '#000000'),
           'http://www.garshol.priv.no/2014/neg/borderline' :
           themap.add_symbol('gray', '#999999', '#000000')}

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT DISTINCT ?s ?lat ?lng ?title ?yeast
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:own-malts ?yeast.
}'''
for (s, lat, lng, title, yeast) in sparqllib.query_for_rows(query):
    symbol = symbols[yeast]
    themap.add_marker(lat, lng, title, symbol)

themap.render_to('own-malts')
