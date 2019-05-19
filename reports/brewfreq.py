
import sparqllib

# ===========================================================================
# GLOBAL

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?h ?c ?s
WHERE {
  ?s dc:title ?title;
    tb:part-of ?c;
    tb:brew-frequency ?h.

  ?c a dbp:Country.
}''' #   FILTER( ?c = dbp:Norway )

values = [float(t) for (t, c, s) in sparqllib.query_for_rows(query)]

# PLOT A HISTOGRAM
# http://matplotlib.org/1.2.1/examples/pylab_examples/histogram_demo.html
from matplotlib import pyplot
(n, bins, patches) = pyplot.hist(values, 10)
pyplot.title('Brews per year')
pyplot.xlabel('Brews')
pyplot.ylabel('Number of accounts')
pyplot.show()

# ===========================================================================
# NORWAY vs DENMARK

def get_data(country):
    query = '''
    prefix dc: <http://purl.org/dc/elements/1.1/>
    prefix neg: <http://www.garshol.priv.no/2014/neg/>
    prefix neu: <http://www.garshol.priv.no/2015/neu/>
    prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
    prefix dbp: <http://dbpedia.org/resource/>
    prefix uff: <http://www.garshol.priv.no/2015/uff/>

    SELECT DISTINCT ?h ?c ?s
    WHERE {
      ?s dc:title ?title;
        tb:part-of ?c;
        tb:brew-frequency ?h.

      ?c a dbp:Country.
      FILTER (?c = dbp:%s)
    }''' % country

    return [float(t) for (t, c, s) in sparqllib.query_for_rows(query)]

# PLOT TWO HISTOGRAMS
# http://stackoverflow.com/questions/6871201/plot-two-histograms-at-the-same-time-with-matplotlib

x = get_data('Denmark')
y = get_data('Norway')

pyplot.hist(x, bins = bins, alpha=0.5, label='dk')
pyplot.hist(y, bins = bins, alpha=0.5, label='no')
pyplot.legend(loc='upper right')
pyplot.title('Brews per year')
pyplot.xlabel('Brews')
pyplot.ylabel('Number of accounts')
pyplot.show()

# ===========================================================================
# BREWFREQ/LATITUDE

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?s ?title ?lat ?freq
WHERE {
  ?s dc:title ?title;
    tb:brew-frequency ?freq;
    geo:lat ?lat.
}'''

x = []
y = []
for (s, title, lat, freq) in sparqllib.query_for_rows(query):
    print title, lat, freq
    x.append(lat)
    y.append(freq)

# SCATTER PLOT
# http://matplotlib.org/examples/shapes_and_collections/scatter_demo.html
from matplotlib import pyplot
h = pyplot.scatter(x, y)
pyplot.title('Brews per year')
pyplot.xlabel('Latitude')
pyplot.ylabel('Number of brews')
pyplot.show()
