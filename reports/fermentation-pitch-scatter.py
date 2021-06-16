
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

SELECT DISTINCT ?s ?lat ?lng ?t ?c ?time
WHERE {
  ?s dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:fermentation-time ?time;
    tb:pitch-temperature ?t.

  ?s tb:part-of ?c.
  ?c a dbp:Country.
}'''

temps = []
times = []
for (s, lat, lng, t, c, time) in sparqllib.query_for_rows(query):
    temp = pitch.get_temp(t)
    if not temp:
        continue

    temps.append(temp)
    times.append(float(time))

from matplotlib import pyplot as plt

plt.scatter(times, temps)
plt.title('Pitch temperature vs fermentation time')
plt.xlabel('Fermentation time')
plt.ylabel('Pitch temperature')
plt.show()
