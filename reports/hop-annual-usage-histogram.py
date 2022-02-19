# encoding=utf-8

import sparqllib
import config

thefilter = ''
if config.get_country():
    thefilter = 'FILTER( ?c = dbp:%s )' % config.get_country()

labels = {
    'en' : {
        'title' : 'Annual hop usage',
        'y-axis' : 'Number of accounts',
        'x-axis' : 'Grams',
    },
    'no' : {
        'title' : u'Årlig forbruk av humle',
        'y-axis' : 'Antall beskrivelser',
        'x-axis' : 'Gram',
    }
}[config.get_language()]

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
    tb:annual-hops-consumption ?h.

  ?c a dbp:Country.
  %s
}''' % thefilter

values = [float(h) for (h, c, s) in sparqllib.query_for_rows(query)]

# PLOT A HISTOGRAM
# http://matplotlib.org/1.2.1/examples/pylab_examples/histogram_demo.html
from matplotlib import pyplot

pyplot.style.use(config.get_plot_style())

(n, bins, patches) = pyplot.hist(values, 10)
pyplot.title(labels['title'])
pyplot.ylabel(labels['y-axis'])
pyplot.xlabel(labels['x-axis'])
if not config.get_file():
    pyplot.show()
else:
    pyplot.savefig(config.get_file())
