
import sparqllib, config, maputils

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?s ?title ?h ?lat ?lng
WHERE {
  ?s dc:title ?title;
    tb:fermentation-time ?h;
    geo:lat ?lat;
    geo:long ?lng.
}
''' #   FILTER (?c = dbp:Norway)

themap = config.make_map_from_cli_args()

symbol_count = 10
smallest = 0
biggest = 250
increment = (biggest - smallest) / symbol_count

if themap.get_color():
    colorfunc = maputils.color
else:
    colorfunc = maputils.bwcolor

symbols = [themap.add_symbol('id%s' % ix,
                             '#' + colorfunc(ix, symbol_count),
                             '#000000',
                             strokeweight = 1,
                             scale = 10,
                             title = '%s-%s' % (smallest + increment*ix, smallest + increment*(ix+1))
           )
           for ix in range(symbol_count)]

for (s, title, h, lat, lng) in sparqllib.query_for_rows(query):
    hours = float(h)

    index = (int((hours - smallest) / increment))
    symbol = symbols[min(index, symbol_count - 1)]
    print hours, min(index, symbol_count - 1), symbol.get_color()
    themap.add_marker(lat, lng, '%s' % title, symbol)

themap.set_legend(True)
themap.render_to('fermentation-time-map')
