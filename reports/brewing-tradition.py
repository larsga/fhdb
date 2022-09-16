
import config
import maplib
import sparqllib

themap = config.make_map_from_cli_args()
labels = {
    'no' : {
        'brewing'    : 'Brygging',
        'nobrew'     : 'Ingen brygging',
        'borderline' : 'I grenseland',
    },
    'en' : {
        'brewing'    : 'Brewing',
        'nobrew'     : 'No brewing',
        'borderline' : 'Borderline',
    },
}[config.get_language()]

brew = themap.add_symbol('#FFFF00', '#000000', strokeweight = 1,
                         title = labels['brewing'])
nobrew = themap.add_symbol('#000000', '#000000', strokeweight = 1,
                           title = labels['nobrew'])
borderline = themap.add_symbol('#AAAAAA', '#000000', strokeweight = 1,
                               title = labels['borderline'])

symbols = {
    '1' : brew,
    '0' : nobrew,
    'true' : brew,
    'false' : nobrew,
    'http://www.garshol.priv.no/2014/neg/borderline' :
        borderline,
#    None : themap.add_symbol('red', '#FF0000', '#000000'),
 }

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT DISTINCT ?s ?lat ?lng ?title ?trad
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:brewing-tradition ?trad.
}'''
for (s, lat, lng, title, trad) in sparqllib.query_for_rows(query):
    themap.add_marker(lat, lng, title, symbols[trad])

themap.set_legend(True)
themap.render_to(config.get_file() or 'brewing-tradition',
                 format = config.get_format())
