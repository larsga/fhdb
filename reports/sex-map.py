
import config
import maplib
import sparqllib

lat = 61.8
lng = 9.45

themap = config.make_map_from_cli_args()

red = themap.add_symbol('red',   '#FF0000', '#000000', strokeweight = 1)
pink = themap.add_symbol('pink', '#FF00FF', '#000000', strokeweight = 1)
blue = themap.add_symbol('blue', '#0000FF', '#000000', strokeweight = 1)

NEG = 'http://www.garshol.priv.no/2014/neg/'
MALE = NEG + 'male'
FEMALE = NEG + 'female'
BOTH = NEG + 'both'
symbol_map = {
    MALE : blue,
    FEMALE : red,
    BOTH : pink
    }

query = '''
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
SELECT ?s ?lat ?lng ?sex ?title
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:brewer-sex ?sex.
}'''
for (s, lat, lng, sex, title) in sparqllib.query_for_rows(query):
    symbol = symbol_map[sex]
    themap.add_marker(lat, lng, title, symbol)

themap.render_to('sex-map.html')
