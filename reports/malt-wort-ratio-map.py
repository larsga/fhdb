
import mapgenlib

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?lat ?lng ?title ?malts
WHERE {
  ?s dc:title ?title;
    tb:malt-wort-ratio ?malts;
    geo:lat ?lat;
    geo:long ?lng.
}'''
mapgenlib.color_scale_map(query, 'malt-wort-ratio-map')
