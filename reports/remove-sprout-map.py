
import config
import maplib
import sparqllib

themap = config.make_map_from_cli_args()

yellow = themap.add_symbol('#FFFF00', '#000000', strokeweight = 1,
                           title = 'Remove')
black = themap.add_symbol('#000000', '#000000', strokeweight = 1,
                          title = "Don't remove")

query = '''
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
SELECT ?s ?lat ?lng ?remove ?title
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    neg:remove-sprout ?remove.
}'''
for (s, lat, lng, remove, title) in sparqllib.query_for_rows(query):
    if remove == 'true':
        symbol = yellow
    elif remove == 'false':
        symbol = black
    else:
        assert 0, 'Bad remove: ' + remove

    themap.add_marker(lat, lng, title, symbol)

themap.set_legend(True)
themap.render_to('remove-sprout-map')
