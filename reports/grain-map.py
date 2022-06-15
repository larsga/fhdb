
import sparqllib, maplib
import config

LEGEND = False
OAT_BELT = False

# ----- STEP 1: COLLECT THE DATA

def strip_uri(uri):
    pos = uri.rfind('/')
    return uri[pos + 1 : ]

data = {} # url -> (lat, lng, [v1, v2, ...])

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
SELECT ?s ?title ?lat ?lng ?grain
WHERE {
  ?s dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng.
    { ?s tb:grain ?grain } UNION { ?s tb:secondary-grain ?grain }
}'''
for (s, title, lat, lng, v) in sparqllib.query_for_rows(query):
    hops = []
    if s in data:
        hops = data[s][-1]
    hops.append(strip_uri(v))

    data[s] = (title, lat, lng, hops)

# ----- STEP 2: MAKE THE MAP

def get_id(url):
    pos = url.rfind('/')
    return url[pos + 1 : -4]

def tostr(grain):
    if len(grain) > 1:
        return ', '.join(grain[ : -1]) + ' and ' + grain[-1]
    else:
        return ', '.join(grain)

NS = 'http://www.garshol.priv.no/2014/neg/'
GEO = 'http://www.w3.org/2003/01/geo/wgs84_pos#'

themap = config.make_map_from_cli_args()

if OAT_BELT:
    geojson = open('/Users/larsga/data/privat/trad-beer/works/map-data/hasund-line.json').read()
    themap.add_line_string(geojson = geojson, color = '#0000FF', width = 3)

mapping = {
    ('barley',)                                  : 'barley',
    ('bere',)                                    : 'barley',
    ('barley', 'oats')                           : 'mixed_oats',
    ('barley', 'rye')                            : 'mixed_rye',
    ('barley', 'rye', 'wheat')                   : 'mixed_rye_wheat',
    ('barley', 'rye', 'oats')                    : 'mixed_rye_oats',
    ('barley', 'oats', 'rye')                    : 'mixed_rye_oats',
    ('barley', 'oats', 'wheat')                  : 'barley_oats_wheat',
    ('barley', 'oats', 'rye', 'wheat')           : 'all_four',
    ('barley', 'wheat')                          : 'barley_wheat',
    ('rye', 'barley')                            : 'mixed_rye',
    ('barley', 'brome', 'oats')                  : 'bizarre',
    ('barley', 'brome', 'oats', 'rye', 'wheat')  : 'bizarre',
    ('emmer', 'spelt')                           : 'bizarre',
    ('oats',)                                    : 'oats',
    ('rye',)                                     : 'rye',
    ('millet',)                                  : 'bizarre',
    }

symbols = {
    'barley' : themap.add_symbol('#00FF00', '#000000', 1),
    'barley_oats_wheat' : themap.add_symbol('#FF55FF', '#000000', 1),
    'barley_wheat' : themap.add_symbol('#FF99FF', '#000000', 1),
    'all_four' : themap.add_symbol('#FF9900', '#000000', 1),
    'mixed_oats' : themap.add_symbol('#FFFF00', '#000000', 1),
    'oats' : themap.add_symbol('#FF0000', '#000000', 1),
    'mixed_rye_oats' : themap.add_symbol('#FFFFFF', '#000000', 1),
    'mixed_rye_wheat' : themap.add_symbol('#BAFFBA', '#000000', 1),
    'mixed_rye' : themap.add_symbol('#00FFFF', '#000000', 1),
    'rye' : themap.add_symbol('#0000FF', '#000000', 1),
    'bizarre' : themap.add_symbol('#000000', '#000000', 1),
    }

mapping = {key : symbols[v] for (key, v) in mapping.items()}

for (s, (title, lat, lng, grain)) in data.items():
    t = title + ': ' + tostr(grain)

    grain = list(set(grain))
    grain.sort()
    grain = tuple(grain)

    themap.add_marker(lat, lng, t, mapping[grain])

themap.set_legend(LEGEND)
themap.render_to('grain-map')
