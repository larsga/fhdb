
import sparqllib
import pitch

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?s ?lat ?lng ?t ?yeast
WHERE {
  ?s dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:pitch-temperature ?t.

  OPTIONAL {
    ?s tb:own-yeast ?yeast
  }
}'''

accounts = set()

own = 0
unknown = 0
other = 0
for (s, lat, lng, t, yeast) in sparqllib.query_for_rows(query):
    if not pitch.get_temp(t):
        continue

    if s in accounts:
        print 'DUPLICATE', s
    accounts.add(s)

    if yeast == 'true':
        own += 1
    elif yeast == 'false':
        other += 1
    else:
        unknown += 1

total = own + unknown + other
print 'Own yeast', own, own / float(total)
print 'Unknown', unknown, unknown / float(total)
print 'Not own yeast', other, other / float(total)
print 'Total', total
