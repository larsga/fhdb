
import sparqllib, config

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
    if data.has_key(s):
        hops = data[s][3]
    hops.append(strip_uri(v))

    data[s] = (t, lat, lng, hops)

# ----- STEP 2: MAKE THE MAP

themap = config.make_map_from_cli_args()

green = themap.add_symbol('green', '#00FF00', '#000000', 1)   # grown
yellow = themap.add_symbol('yellow', '#FFFF00', '#000000', 1) # mixed
red = themap.add_symbol('red', '#FF0000', '#000000', 1)       # bought
white = themap.add_symbol('white', '#FFFFFF', '#000000', 1)   # all three

symbols = {
    ('bought',)                                  : red,
    ('bought', 'gathered-wild')                  : yellow,
    ('locally-grown', 'bought', 'gathered-wild') : yellow,
    ('locally-grown', 'bought')                  : yellow,
    ('gathered-wild', 'bought')                  : yellow,
    ('gathered-wild',)                           : green,
    ('locally-grown', 'gathered-wild')           : green,
    ('locally-grown',)                           : green,
    ('locally-grown', 'gathered-wild', 'bought') : white,
    }

for (s, (title, lat, lng, hops)) in data.items():
    hops = set(hops)
    try:
        themap.add_marker(lat, lng, title, symbols[tuple(hops)], ' '.join(hops))
    except KeyError, e:
        print s
        raise

themap.render_to('hop-growing-map.html')
