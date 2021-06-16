
import sparqllib, config

BINS = 20

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
}''' # tb:pitch-temperature ?pt;

years = []
for (s, title, y) in sparqllib.query_for_rows(query):
    #print s, title, y
    if int(y) < 0:
        print s, title
    years.append(int(y))

years.sort()
print years[0], '-', years[-1]

from matplotlib import pyplot
pyplot.style.use(config.get_plot_style())

(n, bins, patches) = pyplot.hist(years, BINS, alpha=0.5,
                                 label = 'Accounts by year')
pyplot.title('Accounts by year')
pyplot.xlabel('Year')
pyplot.ylabel('Number of accounts')

if not config.get_file():
    pyplot.show()
else:
    pyplot.savefig(config.get_file())
    pyplot.close()
