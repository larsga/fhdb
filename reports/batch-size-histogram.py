#encoding=utf-8

import re
import sparqllib, tablelib

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?s ?title ?t
WHERE {
  ?s dc:title ?title;
    tb:batch-size ?t.
}'''

sizes = [float(t) for (s, title, t) in sparqllib.query_for_rows(query)]

from matplotlib import pyplot
(n, bins, patches) = pyplot.hist(sizes, 30, alpha=0.5,
                                 label = 'Batch sizes')
pyplot.title('Batch sizes')
pyplot.xlabel('Liters')
pyplot.ylabel('Number of accounts')
pyplot.show()
