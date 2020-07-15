#encoding=utf-8

# Reusable logic for interpreting pitch temperature

import re

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

SINGLE = re.compile('(^| |\\()([0-9]?[0-9](\\.[0-9])?)(c|C| (G|g)rader|$)')
RANGE = re.compile('([0-9]?[0-9])-([0-9]?[0-9])(C|c| grader| degrees)?')

MILK = re.compile(u'(mjølk|mælk|milk|mjölk|melk|spen(|e|a)varm(t)?)|mjelk')
MILKTEMP = 36

BODY = re.compile(u'(h(å|a)ndvarm(t|e)|body temperature|kropp?sv(a|ä)rme|blodvarmt|krop(p)?stemperatur|blood heat|blood temperature|human skin)')
BODYTEMP = 37

# https://jamanetwork.com/journals/jama/article-abstract/1155856
SKIN = re.compile(u'human skin')
SKINTEMP = 35.2

# this is not actually enabled
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

    m = SKIN.search(t)
    if m:
        return SKINTEMP

    m = BODY.search(t)
    if m:
        return BODYTEMP

    # m = TALLOW.search(t)
    # if m:
    #     return TALLOWTEMP

    #print repr(t), type(t)

def get_category(t, quiet = True):
    t = t.lower()

    if SINGLE.search(t):
        return 'single'
    elif RANGE.search(t):
        return 'range'
    elif MILK.search(t):
        return 'milkwarm'
    elif SKIN.search(t):
        return 'skin'
    elif BODY.search(t):
        return 'body'
    else:
        if not quiet:
            print 'OTHER:', t
        return 'none'

def get_name(url):
    return sparqllib.query_for_value('''
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

select ?l where { <%s> rdfs:label ?l }''' % url)

def average(numbers):
    return sum(numbers) / len(numbers)
