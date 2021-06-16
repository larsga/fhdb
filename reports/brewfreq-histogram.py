# encoding=utf-8

import config
import sparqllib

BINS = 5

query = '''
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>

SELECT DISTINCT ?s ?ratio
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:brew-frequency ?ratio.

  %s
}'''

if config.get_country():
    query = query % ('?s tb:part-of dbp:' + config.get_country())
else:
    query = query % ''

LANG = config.get_language()
label = {
    'en' : 'Annual brewing frequency',
    'no' : u'Antall brygg pr år'
}

from matplotlib import pyplot

freqs = [float(freq) for (s, freq) in sparqllib.query_for_rows(query)]

pyplot.style.use(config.get_plot_style())
(n, bins, patches) = pyplot.hist(freqs, BINS, alpha=0.5,
                                 label = label[LANG])

pyplot.title(label[LANG])
if LANG == 'en':
    pyplot.xlabel('Brews per year')
    pyplot.ylabel('Number of accounts')
elif LANG == 'no':
    pyplot.xlabel(u'Brygg pr år')
    pyplot.ylabel('Antall beskrivelser')

if config.get_file():
    pyplot.savefig(config.get_file())
else:
    pyplot.show()
