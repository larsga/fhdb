
#encoding=utf-8

import re, codecs, sys
import maplib, mapniklib, sparqllib, mapgenlib

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?s ?lat ?lng ?t ?c
WHERE {
  ?s dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:pitch-temperature ?t.

  ?s tb:part-of ?c.
  ?c a dbp:Country.
}''' # FILTER( ?c = dbp:Estonia)

BINS = 10

SINGLE = re.compile('(^| |\\()([0-9]?[0-9](\\.[0-9])?)(C| (G|g)rader|$)')
RANGE = re.compile('([0-9]?[0-9])-([0-9]?[0-9])(C|c| grader| degrees)?')

MILK = re.compile(u'(mjølk|mælk|milk|mjölk|melk|spen(|e|a)varm(t)?)|mjelk')
MILKTEMP = 36

BODY = re.compile(u'(h(å|a)ndvarm(t|e)|body temperature|kropp?sv(a|ä)rme|blodvarmt|krop(p)?stemperatur|blood heat|blood temperature)')
BODYTEMP = 37

TALLOW = re.compile('(tallow|talg|fra lys)')
TALLOWTEMP = 33

def get_temp(t):
    global singles, ranges, milks, bodies

    m = SINGLE.search(t)
    if m:
        return float(m.group(2))

    m = RANGE.search(t)
    if m:
        low = int(m.group(1))
        high = int(m.group(2))
        return (low + high) / 2.0

    t = t.lower()
    m = MILK.search(t)
    if m:
        return MILKTEMP

    m = BODY.search(t)
    if m:
        return BODYTEMP

    # m = TALLOW.search(t)
    # if m:
    #     return TALLOWTEMP

    print repr(t), type(t)

def get_category(t):
    t = t.lower()

    if SINGLE.search(t) or RANGE.search(t):
        return 'numeric'
    elif MILK.search(t):
        return 'milkwarm'
    elif BODY.search(t):
        return 'body'
    else:
        return 'none'

def get_name(url):
    return sparqllib.query_for_value('''
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

select ?l where { <%s> rdfs:label ?l }''' % url)

def average(numbers):
    return sum(numbers) / len(numbers)

# ===== ALL IN ONE DATA SET

themap = mapniklib.MapnikMap(mapniklib.make_simple_map(
        east = -4, west = 28, south = 52.5, north = 63.5,
        width = 2000, height = 1600
))

symbol_count = 10
symbols = [themap.add_symbol('id%s' % ix,
                             '#' + mapgenlib.color(ix, symbol_count),
                             '#000000',
                             strokeweight = 1,
                             scale = 10
           )
           for ix in range(symbol_count)]

smallest = 0
biggest = 40
increment = (biggest - smallest) / (symbol_count - 1)

for ix in range(10):
    print mapgenlib.color(ix, symbol_count)

for (s, lat, lng, t, c) in sparqllib.query_for_rows(query):
    temp = get_temp(t)
    if temp:
        index = (int((temp - smallest) / increment))
        symbol = symbols[min(index, symbol_count - 1)]
        print temp, min(index, symbol_count - 1), symbol.get_color()
        themap.add_marker(lat, lng, 'No title', symbol)

themap.render_to('pitch-temperature-map.png')
