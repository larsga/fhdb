#encoding=utf-8

import maplib
import sparqllib
import config

lat = 61.8
lng = 9.45

themap = config.make_map_from_cli_args()

LANG = config.get_language()
labels = {'en' : {
        'bottom' : 'Bottom',
        'top' : 'Top',
        'cask' : 'Cask-bottom',
        'either' : 'Either',
    }, 'no' : {
        'bottom' : 'Bunn',
        'top' : 'Topp',
        'cask' : u'Bunn av tønne',
        'either' : 'Bunn/topp',
    }
}

BLACK = themap.add_symbol('#000000', title = labels[LANG]['bottom'])
DARK_GRAY = themap.add_symbol('#555555', '#000000',
                              title = labels[LANG]['cask'])
EITHER = themap.add_symbol('#999999', title = labels[LANG]['either'])
TOP = themap.add_symbol('#FFFF00', title = labels[LANG]['top'])

NEG = 'http://www.garshol.priv.no/2014/neg/'
symbols =  {
    NEG + 'top' : TOP,
    NEG + 'bottom' : BLACK,
    NEG + 'cask-bottom' : DARK_GRAY,
    NEG + 'either' : EITHER,
    NEG + 'both' : EITHER
}

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix eu: <http://www.garshol.priv.no/2017/eu/>
prefix r: <http://www.garshol.priv.no/2014/trad-beer/recipe/>

SELECT DISTINCT ?s ?lat ?lng ?title ?harvest
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:yeast-harvest ?harvest.
}'''
for (s, lat, lng, title, harvest) in sparqllib.query_for_rows(query):
    try:
        symbol = symbols[harvest]
    except KeyError:
        print('KeyError:', s, harvest)
        raise
    themap.add_marker(lat, lng, title, symbol)

themap.set_legend(True)
themap.render_to(config.get_file() or 'yeast-harvest')
