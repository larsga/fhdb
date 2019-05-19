
import mapgenlib

query = '''
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT DISTINCT ?lat ?lng ?title ?ratio
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:brew-frequency ?ratio.

}'''
mapgenlib.color_scale_map(
    query,
    'brewfreq-map.html',
    max_value = 40
)
