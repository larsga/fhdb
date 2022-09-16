#encoding=utf-8

import sparqllib, config

BINS = 20

countryf = ''
if config.get_country():
    countryf = '?s tb:part-of dbp:' + config.get_country()

labels = {
    'en' : {
        'title'    : 'Accounts by year',
        'year'     : 'Year',
        'accounts' : 'Number of accounts',
    },
    'no' : {
        'title'    : 'Beskrivelser etter år',
        'year'     : 'År',
        'accounts' : 'Antall beskrivelser',
    },
}[config.get_language()]

query = '''
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?s ?title ?y
WHERE {
  ?s a ?type;
    dc:title ?title;
    tb:year ?y.

  ?type rdfs:subClassOf tb:Account.
  %s
}''' % countryf

years = []
for (s, title, y) in sparqllib.query_for_rows(query):
    #print s, title, y
    if int(y) < 0:
        print(s, title)
    years.append(int(y))

years.sort()
print(years[0], '-', years[-1])

from matplotlib import pyplot
pyplot.style.use(config.get_plot_style())

(n, bins, patches) = pyplot.hist(years, BINS, label = labels['title'])
pyplot.title(labels['title'])
pyplot.xlabel(labels['year'])
pyplot.ylabel(labels['accounts'])

if not config.get_file():
    pyplot.show()
else:
    pyplot.savefig(config.get_file())
    pyplot.close()
