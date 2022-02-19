
import sys, string
import config
import sparqllib

config.parser.add_argument('--herb', required = True)
config.parser.add_argument('--speciesfile', required = False)

fileformat = config.get_format()
speciesfile = config._get_args().speciesfile
themap = config.make_map_from_cli_args(speciesfile = speciesfile)
herb = config._get_args().herb
show_false = True
LANG = config.get_language()

# ----- GET NAME OF HERB IN CORRECT LANGUAGE

name = None
langmatch = False

query = '''
prefix neg: <http://www.garshol.priv.no/2014/neg/>
select str(?lab) lang(?lab) where {
  neg:%s a neg:Herb;
    rdfs:label ?lab.
}
''' % herb
for (label, lang) in sparqllib.query_for_rows(query):
    if not name:
        name = label
    elif lang == LANG:
        name = label
        langmatch = True

name = name or herb # fallback

# ----- NAME STOP

labeltemplates = {
    'en' : {
        'true' : '%s used',
        'false' : '%s not used',
    },
    'no' : {
        'true' : '%s brukt',
        'false' : '%s ikke brukt',
    },
}[LANG]

white = themap.add_symbol('#FFFF00', '#000000', strokeweight = 1,
                          title = labeltemplates['true'] % name)
black = themap.add_symbol('#000000', '#000000', strokeweight = 1,
                          title = labeltemplates['false'] % name)

query = '''
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT ?s ?title ?lat ?lng ?herbs
WHERE {
  ?s a ?klass;
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:herbs ?herbs.

  ?klass rdfs:subClassOf* tb:Account.
}'''
accounts = {}
has_herb = {}
for (s, title, lat, lng, herbs) in sparqllib.query_for_rows(query):
    has_herb[s] = herbs.endswith('/' + herb) or has_herb.get(s)
    accounts[s] = (title, lat, lng)

dots = []
for (s, (title, lat, lng)) in accounts.items():
    if has_herb[s]:
        symbol = white
    elif not show_false:
        continue
    else:
        symbol = black

    dots.append((lat, lng, title, symbol))

# sort so that the white ones end up on top
if show_false:
    for (lat, lng, title, symbol) in dots:
        if symbol == black:
            themap.add_marker(lat, lng, title, symbol)
for (lat, lng, title, symbol) in dots:
    if symbol == white:
        themap.add_marker(lat, lng, title, symbol)

themap.set_legend(True)
themap.render_to(config.get_file() or 'herb-map', format = fileformat)
