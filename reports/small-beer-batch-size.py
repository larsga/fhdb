#encoding=utf-8

import config
import sparqllib

FILTER = ''
if config.get_country():
    FILTER = '?s tb:part-of dbp:' + config.get_country()

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>

SELECT DISTINCT ?s ?title ?t ?b
WHERE {
  ?s dc:title ?title;
    tb:small-beer-batch-size ?t.

  OPTIONAL { ?s tb:batch-size ?b }

  %s
}''' % FILTER

LANG = config.get_language()

data = list(sparqllib.query_for_rows(query))

ratios = []
for (s, t, small, big) in data:
    ratio = float(small) / float(big)
    print(small, big, ratio)
    ratios.append(ratio)
print('Avg:', sum(ratios) / len(ratios))

x = [float(small) for (s, t, small, big) in data]
y = [float(big) for (s, t, small, big) in data]

from matplotlib import pyplot
pyplot.style.use(config.get_plot_style())

h = pyplot.scatter(x, y)
pyplot.plot([x for x in range(50, 400)],
            [y for y in range(50, 400)],
            'b')

pyplot.xlabel({
    'en' : 'Small beer batch size',
    'no' : 'Liter spissøl',
}[LANG])
pyplot.ylabel({
    'en' : 'Main beer batch size',
    'no' : 'Liter godøl',
}[LANG])
pyplot.title({
    'en' : 'Small beer batch ratio',
    'no' : 'Forholdet mellom godøl og spissøl'
}[LANG])

pyplot.show()


# =====

BINS = 20

(n, bins, patches) = pyplot.hist(ratios, BINS)
# pyplot.title(labels['title'])
# pyplot.xlabel(labels['xlabel'])
# pyplot.ylabel(labels['ylabel'])
pyplot.show()
