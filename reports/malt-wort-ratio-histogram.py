
import sparqllib, config

BINS = 20

labels = {
    'en': {
        'title' : 'Farmhouse ale strength',
        'xlabel' : 'Kilos of malt pr liter',
        'ylabel' : 'Number of accounts',
    },
    'no' : {
        'title' : 'Ølets styrke',
        'xlabel' : 'Kilo malt pr liter',
        'ylabel' : 'Antall beskrivelser',
    }
}[config.get_language()]

thefilter = ''
if config.get_country():
    thefilter = '''
      ?s tb:part-of ?c.
      FILTER( ?c = dbp:%s )
    ''' % config.get_country()

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix sproc: <http://www.garshol.priv.no/2014/trad-beer/simple-process/>

SELECT DISTINCT ?s ?malts
WHERE {
  ?s dc:title ?title;
    tb:malt-wort-ratio ?malts;
    geo:lat ?lat;
    geo:long ?lng.

  %s
}''' % thefilter

ratios = [float(ratio) for (s, ratio) in sparqllib.query_for_rows(query)]

from matplotlib import pyplot

pyplot.style.use(config.get_plot_style())
(n, bins, patches) = pyplot.hist(ratios, BINS,
                                 label = 'Malt/wort ratios')
pyplot.title(labels['title'])
pyplot.xlabel(labels['xlabel'])
pyplot.ylabel(labels['ylabel'])
if not config.get_file():
    pyplot.show()
else:
    pyplot.savefig(config.get_file())
