
import config
import maplib
import sparqllib

themap = config.make_map_from_cli_args()

symbols = {
    '1' : themap.add_symbol('white', '#FFFF00', '#000000', strokeweight = 1),
    '0' : themap.add_symbol('black', '#000000', '#000000', strokeweight = 1),
    'true' : themap.add_symbol('white', '#FFFF00', '#000000', strokeweight = 1),
    'false' : themap.add_symbol('black', '#000000', '#000000', strokeweight = 1),
    'http://www.garshol.priv.no/2014/neg/borderline' :
        themap.add_symbol('gray', '#AAAAAA', '#000000', strokeweight = 1),
#    None : themap.add_symbol('red', '#FF0000', '#000000'),
 }

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT DISTINCT ?s ?lat ?lng ?title ?trad
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:brewing-tradition ?trad.
}'''
for (s, lat, lng, title, trad) in sparqllib.query_for_rows(query):
    themap.add_marker(lat, lng, title, symbols[trad])

themap.render_to(config.get_file() or 'brewing-tradition',
                 format = config.get_format())
