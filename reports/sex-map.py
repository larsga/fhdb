# encoding=utf-8

import config
import maplib
import sparqllib

LANG = config.get_language()
themap = config.make_map_from_cli_args()

labels = {'en' : {
        'women' : 'Women',
        'men' : 'Men',
        'either' : 'Either'
    },
    'no' : {
        'women' : 'Kvinner',
        'men' : 'Menn',
        'either' : 'Begge'
    }
}

l = labels[LANG]
red = themap.add_symbol('#FF0000', '#000000', title = l['women'])
pink = themap.add_symbol('#FF00FF', '#000000', title = l['either'])
blue = themap.add_symbol('#0000FF', '#000000', title = l['men'])

NEG = 'http://www.garshol.priv.no/2014/neg/'
MALE = NEG + 'male'
FEMALE = NEG + 'female'
BOTH = NEG + 'both'
symbol_map = {
    MALE : blue,
    FEMALE : red,
    BOTH : pink
    }

query = '''
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
SELECT ?s ?lat ?lng ?sex ?title
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:brewer-sex ?sex.
}'''
for (s, lat, lng, sex, title) in sparqllib.query_for_rows(query):
    symbol = symbol_map[sex]
    themap.add_marker(lat, lng, title, symbol)

themap.set_legend(True)
themap.render_to(config.get_file() or 'sex-map')
