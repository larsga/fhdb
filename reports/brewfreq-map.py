
import config
import maputils

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
    tb:brew-frequency ?ratio.

  %s
}'''

filter = ''
if config.get_country():
    filter = '?s tb:part-of dbp:' + config.get_country()

maputils.color_scale_map(
    query % filter,
    'brewfreq-map',
    max_value = 40,
    legend = True,
    label_formatter = maputils.format_scale_2_digits
)
