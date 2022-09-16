#encoding=utf-8

import config, maputils

config.parser.add_argument('--max', default = 10 ** 9, type = int)
themax = config._get_args().max

thefilter = ''
if config.get_country():
    thefilter = '?s tb:part-of dbp:%s.' % config.get_country()

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?lat ?lng ?title ?t
WHERE {
  ?s dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:batch-size ?t.

  %s
}''' % thefilter
maputils.color_scale_map(
    query,
    config.get_file() or 'batch-size-map',
    value_mapper = lambda x: min(x, themax),
    legend = True,
)
