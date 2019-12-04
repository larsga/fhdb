
import sparqllib, maplib

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
    if data.has_key(s):
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

lat = 61.8
lng = 9.45

themap = maplib.Map(lat, lng, 6)

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
    ('oats',)                                    : 'oats',
    ('rye',)                                     : 'rye',
    }

symbols = {
    'barley' : themap.add_symbol('barley', '#00FF00', '#000000', 1),
    'barley_oats_wheat' : themap.add_symbol('barley_oats_wheat', '#FF55FF', '#000000', 1),
    'barley_wheat' : themap.add_symbol('barley_wheat', '#FF99FF', '#000000', 1),
    'all_four' : themap.add_symbol('all_four', '#FF9900', '#000000', 1),
    'mixed_oats' : themap.add_symbol('mixed_oats', '#FFFF00', '#000000', 1),
    'oats' : themap.add_symbol('oats', '#FF0000', '#000000', 1),
    'mixed_rye_oats' : themap.add_symbol('mixed_rye_oats', '#FFFFFF', '#000000', 1),
    'mixed_rye_wheat' : themap.add_symbol('mixed_rye_wheat', '#BAFFBA', '#000000', 1),
    'mixed_rye' : themap.add_symbol('mixed_rye', '#00FFFF', '#000000', 1),
    'rye' : themap.add_symbol('rye', '#0000FF', '#000000', 1),
    'bizarre' : themap.add_symbol('bizarre', '#000000', '#000000', 1),
    }

mapping = {key : symbols[v] for (key, v) in mapping.items()}

for (s, (title, lat, lng, grain)) in data.items():
    t = title + ': ' + tostr(grain)

    grain = list(set(grain))
    grain.sort()
    grain = tuple(grain)

    themap.add_marker(lat, lng, t, mapping[grain])

themap.render_to('grain-map.html')

# ----- STEP 3: DRAW THE OATS BELT

# print '<script>'
# print 'var oatbelt_coors = ['
# for line in open('/Users/lars.garshol/data/privat/trad-beer/norge/havrebeltet.txt'):
#     (lng, lat) = line.strip().split(',')
#     print '  new google.maps.LatLng(%s, %s),' % (lat, lng)
# print '];'

# print '''
# var oatbelt = new google.maps.Polyline({
#     path: oatbelt_coors,
#     geodesic: true,
#     strokeColor: '#FF0000',
#     strokeOpacity: 1.0,
#     strokeWeight: 2
#   });

# oatbelt.setMap(map);
# </script>
# '''
