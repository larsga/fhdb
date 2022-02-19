
import maputils, config

thefilter = ''
if config.get_country():
    thefilter = '?s tb:part-of dbp:%s' % config.get_country()

query = '''
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>

SELECT DISTINCT ?lat ?lng ?title ?ratio
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:hop-wort-ratio ?ratio.

  %s
}''' % thefilter
maputils.color_scale_map(query, config.get_file() or 'hop-ratio-map',
                         legend = True, value_mapper = lambda v: v)
