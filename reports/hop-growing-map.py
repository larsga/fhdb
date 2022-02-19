# encoding=utf-8

import sparqllib, config, maplib

OAT_BELT = False

labels = {
    'en' : {
        'grown' : 'Grown',
        'both' : 'Both',
        'bought' : 'Bought',
        'grown-w' : 'Grown and picked wild',
        'both-w' : 'Both (incl. wild)',
    },
    'no' : {
        'grown' : 'Dyrket',
        'grown-w' : 'Dyrket og plukket vill',
        'both' : 'Begge',
        'both-w' : 'Begge (også vill)',
        'bought' : 'Kjøpt',
    },
}[config.get_language()]

# ----- STEP 1: COLLECT THE DATA

def strip_uri(uri):
    pos = uri.rfind('/')
    return uri[pos + 1 : ]

data = {} # url -> (title, lat, lng, [v1, v2, ...])

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
SELECT ?s ?t ?lat ?lng ?hops
WHERE {
  ?s
    dc:title ?t;
    geo:lat ?lat;
    geo:long ?lng;
    tb:hops ?hops.
}'''
for (s, t, lat, lng, v) in sparqllib.query_for_rows(query):
    hops = []
    if s in data:
        hops = data[s][3]
    hops.append(strip_uri(v))

    data[s] = (t, lat, lng, hops)

# ----- STEP 2: MAKE THE MAP

themap = config.make_map_from_cli_args()

if OAT_BELT:
    geojson = open('/Users/larsga/data/privat/trad-beer/works/map-data/hasund-line.json').read()
    themap.add_line_string(geojson = geojson, color = '#0000FF', width = 3)

sw = 1
green = themap.add_symbol('#00FF00', '#000000', sw, labels['grown'])
green_tr = themap.add_symbol('#00FF00', '#000000', sw, labels['grown-w'],
                             shape = maplib.TRIANGLE)
yellow = themap.add_symbol('#FFFF00', '#000000', sw, labels['both'])
yellow_tr = themap.add_symbol('#FFFF00', '#000000', sw, labels['both-w'],
                              shape = maplib.TRIANGLE)
red = themap.add_symbol('#FF0000', '#000000', sw, labels['bought'])

symbols = {
    ('bought',)                                  : red,
    ('bought', 'gathered-wild')                  : yellow_tr,
    ('bought', 'gathered-wild', 'locally-grown') : yellow_tr,
    ('bought', 'locally-grown')                  : yellow,
    ('gathered-wild',)                           : green,
    ('gathered-wild', 'locally-grown')           : green_tr,
    ('locally-grown',)                           : green,
    }

for (s, (title, lat, lng, hops)) in data.items():
    hops = list(set(hops))
    hops.sort()
    try:
        themap.add_marker(lat, lng, title, symbols[tuple(hops)], ' '.join(hops))
    except KeyError:
        print(s)
        raise

themap.set_legend(True)
themap.render_to(config.get_file() or 'hop-growing-map')
