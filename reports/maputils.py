#encoding=utf-8

import random, string
import maplib
import sparqllib
import config

def random_id():
    return ''.join([random.choice(string.letters) for ix in range(10)])

def matches(regex, s):
    m = regex.match(s)
    return m and len(m.group()) == len(s)

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?title ?lat ?lng ?term
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    %s ?term.
}'''

def make_term_map(termprop, symbols, filename, usemap = None, scale = None):
    global lat, lng
    # symbols: [(regex, color, name), ...]

    stroke = '#000000'

    themap = usemap or config.make_map_from_cli_args()
    symbols = [(regex, themap.add_symbol(random_id(), color, stroke, strokeweight = 1, title = name, scale = scale))
               for (regex, color, name) in symbols]

    OTHER = themap.add_symbol('black', '#000000', stroke, strokeweight = 1,
                              title = 'Other', scale = scale)

    unmatched = []
    for (title, lat, lng, term) in sparqllib.query_for_rows(query % termprop):
        symbol = OTHER
        for (regex, s) in symbols:
            if matches(regex, term):
                symbol = s
                break

        themap.add_marker(lat, lng, title + ': ' + term, symbol)
        if symbol == OTHER:
            unmatched.append(term)

    themap.set_legend(True)
    themap.render_to(filename)

    unmatched.sort()
    for term in unmatched:
        print term

def make_thing_map(query, symbols, filename, legend = False):
    global lat, lng
    # symbols: [(uri, color, name), ...]

    themap = config.make_map_from_cli_args()
    symbols = {
        uri : (themap.add_symbol(random_id(), color, '#000000', 1, title = name), name)
        for (uri, color, name) in symbols
    }
    other = themap.add_symbol(random_id(), '#000000', '#000000', 1, title = 'Other')

    for (s, title, thing, lat, lng) in sparqllib.query_for_rows(query):
        try:
            (symbol, name) = symbols[thing]
        except KeyError:
            print 'Unclassified:', thing
            symbol = other
            name = thing

        themap.add_marker(lat, lng, title + ': ' + name, symbol)

    themap.set_legend(legend)
    themap.render_to(filename)
