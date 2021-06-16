#encoding=utf-8

import sparqllib, tablelib, sys, config
from numlib import *

BINS = 10

NEG = 'http://www.garshol.priv.no/2014/neg/'

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?s ?h
WHERE {
  ?s dc:title ?title;
    tb:fermentation-time ?h.
}
'''

times = [float(t) for (s, t) in sparqllib.query_for_rows(query)]

import numpy
from matplotlib import pyplot
pyplot.style.use(config.get_plot_style())

(n, bins, patches) = pyplot.hist(
    times, BINS, alpha=0.5,
    label = 'Fermentation times'
)
pyplot.title('Fermentation times')
pyplot.xlabel('Hours')
pyplot.ylabel('Number of accounts')
pyplot.show()
