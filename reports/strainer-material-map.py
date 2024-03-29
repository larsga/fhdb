
import sys, string
import config
import sparqllib

config.parser.add_argument('material', nargs = '?')
material = config._get_args().material

themap = config.make_map_from_cli_args()

white = themap.add_symbol('#FFFFFF', '#000000', strokeweight = 1,
                          title = material[0].upper() + material[1 : ])
black = themap.add_symbol('#000000', '#000000', strokeweight = 1,
                          title = 'No ' + material)

query = '''
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT ?s ?title ?lat ?lng ?herbs
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:strainer ?herbs.
}'''
accounts = {}
has_herb = {}
for (s, title, lat, lng, herbs) in sparqllib.query_for_rows(query):
    has_herb[s] = herbs.endswith('/' + material) or has_herb.get(s)
    accounts[s] = (title, lat, lng)

for (s, (title, lat, lng)) in accounts.items():
    if has_herb[s]:
        symbol = white
    else:
        symbol = black
    themap.add_marker(lat, lng, title, symbol)

themap.set_legend(True)
themap.render_to('strainer-material-map')
