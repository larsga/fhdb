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
    tb:fermentation-time ?h
    %s .
}
'''

if config.get_country():
    f = '; tb:part-of dbp:%s' % config.get_country()
else:
    f = ''
query = query % f

times = [float(t) for (s, t) in sparqllib.query_for_rows(query)]

(title, xlab, ylab) = {
    'en' : ('Fermentation times', 'Hours', 'Number of accounts'),
    'no' : (u'Gjæringstider', 'Timer', 'Antall beskrivelser'),
}[config.get_language()]

import numpy
from matplotlib import pyplot
pyplot.style.use(config.get_plot_style())

(n, bins, patches) = pyplot.hist(
    times, BINS, label = title
)
pyplot.title(title)
pyplot.xlabel(xlab)
pyplot.ylabel(ylab)

if not config.get_file():
    pyplot.show()
else:
    pyplot.savefig(config.get_file())
    pyplot.close()
