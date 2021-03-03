
import sparqllib

# DATABASE IN GENERAL
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
    tb:fg ?h.

  ?c a dbp:Country.
}

''' #   FILTER (?c = dbp:Norway)

values = [float(t) for (t, c, s) in sparqllib.query_for_rows(query)]

# PLOT A HISTOGRAM
# http://matplotlib.org/1.2.1/examples/pylab_examples/histogram_demo.html
from matplotlib import pyplot
h = pyplot.hist(values, 25)
pyplot.title('Final gravities')
pyplot.xlabel('Specific gravity')
pyplot.ylabel('Number of accounts')
pyplot.show()
