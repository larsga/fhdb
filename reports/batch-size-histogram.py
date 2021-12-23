#encoding=utf-8

import config
import sparqllib

BINS = 30
FILTER = ''
if config.get_country():
    FILTER = '?s tb:part-of dbp:%s' % config.get_country()
    BINS = 10

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>

SELECT DISTINCT ?s ?title ?t
WHERE {
  ?s dc:title ?title;
    tb:batch-size ?t.

  %s
}''' % FILTER

labels = {
    'en' : {
        'title': 'Batch sizes',
        'liters' : 'Liters',
        'num' : 'Number of accounts',
    },
    'no' : {
        'title': u'Størrelse på brygg',
        'liters' : 'Liter',
        'num' : 'Antall beskrivelser',
    },
}[config.get_language()]

sizes = [float(t) for (s, title, t) in sparqllib.query_for_rows(query)]

from matplotlib import pyplot
pyplot.style.use('ggplot')

(n, bins, patches) = pyplot.hist(sizes, BINS, label = labels['title'])
pyplot.title(labels['title'])
pyplot.xlabel(labels['liters'])
pyplot.ylabel(labels['num'])

if not config.get_file():
    pyplot.show()
else:
    pyplot.savefig(config.get_file())
    pyplot.close()
