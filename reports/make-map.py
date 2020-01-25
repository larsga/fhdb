'''
Creates a map of all the accounts in the database. It requires the account
to have a latitude and longitude, and to be of a type that is rdfs:subClassOf
tb:Account.
'''

import sys
import maplib
import sparqllib

def extract_number(uri):
    pos = uri.rfind('/')
    pos2 = uri.rfind('.')
    return uri[pos + 1 : pos2]

if len(sys.argv) > 1 and sys.argv[1] == 'png':
    import config
    themap = config.make_europe_all_map()
    scale = 8
else:
    themap = maplib.GoogleMap(62, 15, 5)
    scale = 5

def symbol(id, color):
    return themap.add_symbol(id, color, '#000000', WEIGHT, scale = scale)

WEIGHT = 1

PREFIX = 'http://www.garshol.priv.no/'
symbols = {
    PREFIX + '2014/neg/Response' : symbol('green', '#00FF00'),
    PREFIX + '2015/neu/Item' : symbol('blue', '#5555FF'),
    PREFIX + '2014/trad-beer/Recipe' : symbol('black', '#000000'),
    PREFIX + '2016/dot/DataPoint' : symbol('gray', '#AAAAAA'),
    PREFIX + '2017/eu/Response' : symbol('yellow', '#FFFF00'),
    PREFIX + '2017/eu/PseudoResponse' : symbol('yellow', '#FFFF00'),
    PREFIX + '2017/eu/HopResponse' : symbol('darkgray', '#666666'),
    PREFIX + '2015/sls/Response' : symbol('cyan', '#00FFFF'),
    PREFIX + '2015/uff/Communication' : symbol('red', '#FF0000'),
    PREFIX + '2018/sm/Account' : symbol('paleblue', '#AAAAFF'),
    PREFIX + '2016/km/Account' : symbol('orange', '#FFAA00'),
    PREFIX + '2016/voko/Manuskript' : symbol('pink', '#FF00FF'),
    PREFIX + '2017/eu/HopResponse' : symbol('pink', '#FF00FF'),
    PREFIX + '2015/luf/Response' : symbol('white', '#FFFFFF'),
    PREFIX + '2019/erm/Account' : symbol('paleblue2', '#AFEEEE'),
    PREFIX + '2019/erm/PseudoAccount' : symbol('paleblue2', '#AFEEEE'),
}

query = '''
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
SELECT ?s ?lat ?lng ?title ?t
WHERE {
  ?s a ?t;
    geo:lat ?lat;
    geo:long ?lng.

  ?t rdfs:subClassOf* tb:Account.
  OPTIONAL { ?s dc:title ?title }
}'''
for (s, lat, lng, title, t) in sparqllib.query_for_rows(query):
    if t in symbols:
        themap.add_marker(lat, lng, title or 'No title', symbols[t])
    else:
        print 'NO SYMBOL FOR', t

# ===== RENDER

themap.render_to('map')
