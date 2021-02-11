
import sys, string
import config
import colorsys
import maputils
import sparqllib

fileformat = sys.argv[4] if len(sys.argv) >= 5 else 'png'
speciesfile = sys.argv[3] if len(sys.argv) >= 4 else None
themap = config.make_map_from_cli_args(speciesfile = speciesfile)
herb = sys.argv[2]

white = themap.add_symbol('white', '#FFFFFF', '#000000', strokeweight = 1,
                          title = string.upper(herb[0]) + herb[1 : ])
black = themap.add_symbol('black', '#000000', '#000000', strokeweight = 1,
                          title = 'No ' + herb)

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
    tb:herbs ?herbs.
}'''
accounts = {}
has_herb = {}
for (s, title, lat, lng, herbs) in sparqllib.query_for_rows(query):
    has_herb[s] = herbs.endswith('/' + herb) or has_herb.get(s)
    accounts[s] = (title, lat, lng)

for (s, (title, lat, lng)) in accounts.items():
    if has_herb[s]:
        symbol = white
    else:
        symbol = black

    #themap.add_marker(lat, lng, title, symbol)

themap.set_legend(True)
themap.render_to('herb-map', format = fileformat)
