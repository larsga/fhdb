
import sparqllib
import config
import re

BINS = 20
MAX_VALUE = 800

thefilter = ''
if config.get_country():
    thefilter = 'FILTER( ?c = dbp:%s )' % config.get_country()

labels = {
    'en' : {
        'title' : 'Mash times in farmhouse ale',
        'y-axis' : 'Number of accounts',
        'x-axis' : 'Time in minutes',
    },
    'no' : {
        'title' : 'Mesketider',
        'y-axis' : 'Antall beskrivelser',
        'x-axis' : 'Tid i minutter',
    }
}[config.get_language()]

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>

SELECT DISTINCT ?h ?c ?s
WHERE {
  ?s dc:title ?title;
    tb:part-of ?c;
    neg:mash-time ?h.

  ?c a dbp:Country.
  %s
}''' % thefilter

REG_NUMBER = re.compile('^\\d+(\\.\\d+)?$')
REG_HOURS = re.compile('^(\\d+(\\.\\d+)?) hour(s)?$')
REG_HOUR_RANGE = re.compile('^(\\d+)-(\\d+) hour(s)?$')

def convert(s, t):
    m = REG_NUMBER.match(t)
    if m:
        t = float(m.group())
        if t < 30:
            print('time:', t, s)
        return t

    m = REG_HOURS.match(t)
    if m:
        return float(m.group(1)) * 60

    m = REG_HOUR_RANGE.match(t)
    if m:
        return ((float(m.group(1)) + float(m.group(2))) / 2) * 60

    print("Can't interpret", t, s)

values = [convert(s, h) for (h, c, s) in sparqllib.query_for_rows(query)]
values = [h for h in values if h and h < MAX_VALUE]

# PLOT A HISTOGRAM
# http://matplotlib.org/1.2.1/examples/pylab_examples/histogram_demo.html
from matplotlib import pyplot

pyplot.style.use(config.get_plot_style())

(n, bins, patches) = pyplot.hist(values, BINS)
pyplot.title(labels['title'])
pyplot.ylabel(labels['y-axis'])
pyplot.xlabel(labels['x-axis'])
if not config.get_file():
    pyplot.show()
else:
    pyplot.savefig(config.get_file())
