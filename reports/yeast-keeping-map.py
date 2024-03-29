# encoding=utf-8

import colorsys
import config
import sparqllib

themap = config.make_map_from_cli_args()

LANG = config.get_language()
labels = {'en' : {
        'other' : 'Other',
        'cakes' : 'Yeast cakes',
        'log'   : 'Yeast log',
        'ring'  : 'Yeast ring',
        'dried' : 'Dried',
        'cask'  : 'Cask bottom',
        'wet'   : 'Wet',
    }, 'no' : {
        'other' : 'Annet',
        'cakes' : u'Gjærkaker',
        'log'   : u'Gjærstokk',
        'ring'  : u'Gjærkrans',
        'dried' : u'Tørket',
        'cask'  : 'Bunn av fat',
        'wet'   : u'Våt',
    }
}

black = themap.add_symbol('#000000', '#000000', strokeweight = 1,
                          title = labels[LANG]['other'])
yellow = themap.add_symbol('#FFAAAA', '#000000', strokeweight = 1, title = labels[LANG]['cakes'])
dark_yellow = themap.add_symbol('#AAAAFF', '#000000', strokeweight = 1, title = labels[LANG]['log'])
dark_yellow2 = themap.add_symbol('#FFFFAA', '#000000', strokeweight = 1, title = labels[LANG]['ring'])
brown = themap.add_symbol('#C04343', '#000000', strokeweight = 1,
                          title = labels[LANG]['dried'])
#white = themap.add_symbol('white', '#FFFFFF', '#000000', strokeweight = 1)
green = themap.add_symbol('#00FF00', '#000000', strokeweight = 1,
                          title = labels[LANG]['cask'])
#red = themap.add_symbol('#FF0000', '#000000', strokeweight = 1)
#dark_red = themap.add_symbol('dark_red', '#AA0000', '#000000', strokeweight = 1)
blue = themap.add_symbol('#4444FF', '#000000', strokeweight = 1,
                         title = labels[LANG]['wet'])
symbols = {
    'Dried in a trough'           : brown,
    'Dried in a trough with potato flour' : brown,
    'Dried on bricks'             : brown,
    'Dried on hops'               : brown,
    'Yeast dried on a hair sieve' : brown,
    'Straw ring with hops'        : brown,
    'Straw ring'                  : brown,
    'Dried on straw (not a ring)' : brown,
    'Dried in a jar'              : brown,
    'Dried in a cup'              : brown,
    'Dried in fermentor'          : brown,
    'Dried on wooden boards'      : brown,
    'Dried on wooden boards with hops' : brown,
    'Dried next to oven'          : brown,
    'Dried on cloth'              : brown,
    'Dried on flatbread'          : brown,
    'Dried on branches'           : brown,
    'Dried, kept in cloth bag'    : brown,
    'Dried in a trough, kept in cloth bag' : brown,
    'Dried on cloth on top of ash' : brown,
    'Dried on a withy'            : brown,
    'Dried on a plate'            : brown,
    'Dried on stones'             : brown,
    'In a bowl'                   : brown,
    'Kneaded into flour, stored dried in jar' : brown,

    'Yeast log'                   : dark_yellow,
    'Yeast ring'                  : dark_yellow2,
    u'Gj\xe6rkrans'               : dark_yellow2,

    'Yeast cakes' : yellow,

    'A jar in the well' : blue,
    'Buried jar'        : blue,
    'Jar stored in ice' : blue,
    'In a jar'          : blue,
    'In corked bottle'  : blue,
    'In a bucket'  : blue,

    'From bottom of beer cask' : green,
}

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix yeast: <http://www.garshol.priv.no/2017/trad-beer/yeast-keeping/>

SELECT DISTINCT ?s ?lat ?lng ?proc ?procname ?title
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:yeast-keeping ?proc.

  ?proc rdfs:label ?procname.
}'''# FILTER( ?proc in (yeast:log, yeast:yeast-ring))

for (s, lat, lng, proc, procname, title) in sparqllib.query_for_rows(query):
    symbol = symbols.get(procname, black)
    if symbol == black:
        print('UNMAPPED', repr(procname))

    themap.add_marker(lat, lng, title, symbol, procname)

themap.set_legend(True)
themap.render_to(config.get_file() or 'yeast-keeping-map')
