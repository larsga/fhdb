
import config
import maplib
import sparqllib

themap = config.make_map_from_cli_args()

labels = {
    'no' : {
        'made' : 'Kvas laget',
        'notmade' : 'Ingen kvas',
    },
    'en' : {
        'made' : 'Kvass made',
        'notmade' : 'No kvass',
    }
}[config.get_language()]

made = themap.add_symbol('#FFFF00', '#000000', title = labels['made'])
notmade = themap.add_symbol('#000000', '#000000', title = labels['notmade'])
symbols = {
    '1' : made,
    '0' : notmade,
    'true' : made,
    'false' : notmade
}

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT DISTINCT ?s ?lat ?lng ?title ?mead
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:kvass ?mead.
}'''
for (s, lat, lng, title, mead) in sparqllib.query_for_rows(query):
    themap.add_marker(lat, lng, title, symbols[mead])

themap.set_legend(True)
themap.render_to(config.get_file() or 'kvass-map')
