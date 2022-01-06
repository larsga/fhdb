# encoding=utf-8

import config
import sparqllib

def number(boolean):
    if boolean == 'http://www.garshol.priv.no/2014/neg/borderline':
        return 0.5
    elif boolean == 'true':
        return 1.0
    elif boolean == 'false':
        return 0.0
    else:
        return int(boolean)

themap = config.make_map_from_cli_args()
LANG = config.get_language()

labels = {
'en' : {
    'infusion' : 'Infusion',
    'none' : 'No juniper',
    'filter' : 'Filter only'
    },
'no' : {
    'infusion' : u'Einerlåg',
    'none' : 'Ingen einer',
    'filter' : 'Bare i rost'
    },
}[LANG]

white = themap.add_symbol('white', '#FFFFFF', '#000000', strokeweight = 1,
                          title = labels['infusion'])
black = themap.add_symbol('black', '#000000', '#000000', strokeweight = 1,
                          title = labels['none'])
gray = themap.add_symbol('gray', '#BBBBBB', '#000000', strokeweight = 1,
                         title = labels['filter'])
symbols = {1 : white, 0 : black, 0.5 : gray}

query = '''
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
SELECT ?s ?title ?lat ?lng ?inf
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:juniper-infusion ?inf.
}'''
accounts = { s : (title, lat, lng, number(inf))
             for (s, title, lat, lng, inf) in sparqllib.query_for_rows(query) }

query = '''
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT ?s ?title ?lat ?lng ?herbs
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:herbs ?herbs.
}'''
for (s, title, lat, lng, herbs) in sparqllib.query_for_rows(query):
    if herbs.endswith('/juniper'):
        is_juniper = 0.5
    else:
        is_juniper = 0

    if s in accounts:
        is_juniper = max(accounts[s][3], is_juniper)

    accounts[s] = (title, lat, lng, is_juniper)

for (title, lat, lng, juniper) in accounts.values():
    themap.add_marker(lat, lng, title, symbols[juniper])

themap.set_legend(True)
themap.render_to(config.get_file() or 'juniper-map')
