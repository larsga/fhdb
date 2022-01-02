#encoding=utf-8
'''
NOTE: Only own yeast included!
'''

import sys
import sparqllib
import pitch
import config

BINS = 10
year = sys.argv[1]
LANG = config.get_language()

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?s ?lat ?lng ?t
WHERE {
  ?s dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:pitch-temperature ?t;
    tb:yeast-type neg:own-yeast;
    tb:year ?year.

  %s
  FILTER (?year %s %s)
}'''

country = ''
if config.get_country():
    country = '?s tb:part-of dbp:' + config.get_country() + ' . '

before = []
after = []
lowest = 10000
highest = 0
for (s, lat, lng, t) in sparqllib.query_for_rows(query % (country, '<', year)):
    temp = pitch.get_temp(t)

    if temp:
        before.append(temp)
        lowest = min(temp, lowest)
        highest = max(temp, highest)

for (s, lat, lng, t) in sparqllib.query_for_rows(query % (country, '>=', year)):
    temp = pitch.get_temp(t)

    if temp:
        after.append(temp)
        lowest = min(temp, lowest)
        highest = max(temp, highest)

import numpy
from matplotlib import pyplot

labels = {'en' : {
    'degrees' : 'Degrees C',
    'accounts' : 'Number of accounts',
    'before' : 'Pitch temperatures before',
    'after' : 'Pitch temperatures after',
    },
    'no' : {
    'degrees' : 'Grader C',
    'accounts' : 'Antall beskrivelser',
    'before' : u'Tilsetningstemperaturer før',
    'after' : 'Tilsetningstemperaturer etter',
    },
}

def plot(label, temperatures, ix, lowest, highest):
    pyplot.style.use('ggplot')
    (n, bins, patches) = pyplot.hist(
        temperatures, BINS,
        label = label,
        range = (lowest, highest)
    )
    pyplot.title(label)
    pyplot.xlabel(labels[LANG]['degrees'])
    pyplot.ylabel(labels[LANG]['accounts'])

    pyplot.savefig('pitch-%s.png' % ix)
    pyplot.close()

plot('%s %s' % (labels[LANG]['before'], year), before, 0, lowest, highest)
plot('%s %s' % (labels[LANG]['after'], year), after, 1, lowest, highest)

# --- Combine

import imglib
imglib.tile_images(
    imagelist = [('pitch-%s.png' % i) for i in range(2)],
    rows = [[0, 1]],
    outfile = config.get_file() or 'pitch-temperature-histogram-by-year.png'
)
