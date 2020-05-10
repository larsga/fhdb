
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

SELECT DISTINCT ?s ?lat ?lng ?t ?c ?year
WHERE {
  ?s dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:year ?year;
    tb:pitch-temperature ?t.

  ?s tb:part-of ?c.
  ?c a dbp:Country.
}'''

temps = []
years = []
for (s, lat, lng, t, c, year) in sparqllib.query_for_rows(query):
    temp = pitch.get_temp(t)
    if not temp:
        continue

    temps.append(temp)
    years.append(int(year))

# first, count the number of times each combination appears
counts = {}
for key in zip(temps, years):
    counts[key] = counts.get(key, 0) + 1
for (key, count) in counts.items():
    if count > 1:
        print key, count

# then, produce the size array
sizes = []
for key in zip(temps, years):
    sizes.append(counts[key] * 10)

from matplotlib import pyplot as plt

plt.scatter(years, temps, s = sizes)
plt.title('Publication year vs pitch temperature')
plt.xlabel('Publication year')
plt.ylabel('Pitch temperature')
plt.show()
