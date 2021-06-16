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

def make_term_map(termprop, symbols, filename, usemap = None, scale = None,
                  language = 'en'):
    global lat, lng
    # symbols: [(regex, color, name), ...]

    stroke = '#000000'

    themap = usemap or config.make_map_from_cli_args()
    symbols = [(regex, themap.add_symbol(random_id(), color, stroke, strokeweight = 1, title = name, scale = scale))
               for (regex, color, name) in symbols]

    othername = {
        'en' : 'Other',
        'no' : 'Annet',
    }[language]
    OTHER = themap.add_symbol('black', '#000000', stroke, strokeweight = 1,
                              title = othername, scale = scale)

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

def make_boolean_map(query, filename, labels = None):
    themap = config.make_map_from_cli_args()
    if labels:
        themap.set_legend(True)
    labels = labels or {'borderline' : '', 'true' : '', 'false' : ''}

    gray = themap.add_symbol('gray', '#999999', title = labels['borderline'])
    symbols = {
        'true' : themap.add_symbol('white', '#FFFF00', title = labels['true']),
        'false' : themap.add_symbol('black', '#000000', title = labels['false']),
        'http://www.garshol.priv.no/2014/neg/both' : gray,
        'http://www.garshol.priv.no/2014/neg/borderline' : gray}

    for (s, lat, lng, title, value) in sparqllib.query_for_rows(query):
        symbol = symbols[value]
        themap.add_marker(lat, lng, title, symbol)

    themap.render_to(filename)

import config
import colorsys
import maplib
import sparqllib
import math

def chex(color):
    return hex(int(color * 255))[2 : ].zfill(2)

def rgb(hue, saturation, vrightness):
    (r, g, b) = colorsys.hsv_to_rgb(hue, saturation, vrightness)
    return chex(r) + chex(g) + chex(b)

def color(index, symbols):
    import colormaps
    # ratio = math.log(value + 1) / math.log(symbols)
    # return chex(ratio) + chex(ratio) + chex(ratio)

    inc = len(colormaps._magma_data) / float(symbols)
    ix = int(round(inc * index))

    (r, g, b) = colormaps._magma_data[ix]
    return chex(r) + chex(g) + chex(b)

def bwcolor(index, symbols):
    brightness = (index / float(symbols))
    return chex(brightness) + chex(brightness) + chex(brightness)

# ===== COLOR SCALE MAP

# these are essentially parameters
symbol_count = 256
max_scale = 25

def value_mapper(v):
    'Remap values for better visualization.'
    return math.log(v)

def color_scale_map(query, outfile, max_value = 1000000, legend = False,
                    symbol_count = 10, value_mapper = value_mapper,
                    label_formatter = lambda y,x: '%s-%s' % (y,x)):
    data = [(lat, lng, title, value_mapper(min(float(ratio), max_value)))
            for (lat, lng, title, ratio) in sparqllib.query_for_rows(query)]
    color_scale_map_data(data, outfile, legend, symbol_count,
                         label_formatter)

def format_scale_2_digits(low, high):
    low = int(round(low * 10.0)) / 10.0
    high = int(round(high * 10.0)) / 10.0
    return '%s-%s' % (low, high)

def color_scale_map_data(data, outfile, legend = False, symbol_count = 10,
                         label_formatter = None, the_range = None):
    themap = config.make_map_from_cli_args()

    if the_range:
        (smallest, biggest) = the_range
    else:
        smallest = min([v for (lat, lng, title, v) in data])
        biggest = max([v for (lat, lng, title, v) in data])

    increment = (biggest - smallest) / (symbol_count - 1)
    symbols = [themap.add_symbol(
        'id%s' % ix,
        '#' + color(ix, symbol_count),
        '#000000',
        strokeweight = 1,
        title = label_formatter(smallest + increment * ix,
                                smallest + increment * (ix+1))
        #,scale = (ix / float(symbol_count)) * max_scale
    )
    for ix in range(symbol_count)]

    for (lat, lng, title, org_value) in data:
        ratio = org_value
        index = (int((ratio - smallest) / increment))
        symbol = symbols[index]
        themap.add_marker(lat, lng, title, symbol, 'Value: %s' % org_value)

    themap.set_legend(legend)
    themap.render_to(outfile)
