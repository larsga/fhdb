
import sys, os
import colorsys
import config
import maputils
import sparqllib

themap = config.make_map_from_cli_args()
LANG = config.get_language()

labels = {
    'en' : {
        'boiled' : 'Boiled',
        'notboiled' : 'Not boiled',
        'borderline' : 'Borderline',
    },
    'no' : {
        'boiled' : 'Kokt',
        'notboiled' : 'Ikke kokt',
        'borderline' : 'På grensen',
    }
}[LANG]

stroke = 1
istrue = themap.add_symbol('boiled', '#FFFF00', '#000000',
                           strokeweight = stroke,
                           title = labels['boiled'])
isfalse = themap.add_symbol('notboiled', '#000000', '#000000',
                            strokeweight = stroke,
                            title = labels['notboiled'])
borderline = themap.add_symbol('borderline', '#AAAAAA', '#000000',
                               strokeweight = stroke,
                               title = labels['borderline'])

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix sproc: <http://www.garshol.priv.no/2014/trad-beer/simple-process/>

SELECT DISTINCT ?s ?lat ?lng ?title ?procname ?aspect
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:process ?proc.

  ?proc
    rdfs:label ?procname;
    tb:wort-boiled ?aspect.
}'''

for (s, lat, lng, title, procname, aspect) in sparqllib.query_for_rows(query):
    desc = '<b>%s</b><br>Process %s' % (title, procname)

    symbol = None
    if aspect == 'true':
        symbol = istrue
    elif aspect == 'false':
        symbol = isfalse
    else:
        symbol = borderline

    themap.add_marker(lat, lng, title, symbol, desc)

themap.set_legend(True)
themap.render_to(config.get_file() or 'wort-boil-map')
