#encoding=utf-8

import sparqllib
import pitch

BINS = 10

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?s ?lat ?lng ?t ?harvest
WHERE {
  ?s dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:pitch-temperature ?t;
    tb:yeast-harvest ?harvest.
}'''

NAMES = {
    'http://www.garshol.priv.no/2014/neg/top' : 'top',
    'http://www.garshol.priv.no/2014/neg/bottom' : 'bottom',
}

groups = {}
lowest = 10000
highest = 0
for (s, lat, lng, t, harvest) in sparqllib.query_for_rows(query):
    temp = pitch.get_temp(t)

    if temp and harvest in NAMES:
        if harvest not in groups:
            groups[harvest] = []
        groups[harvest].append(temp)
        lowest = min(temp, lowest)
        highest = max(temp, highest)

import numpy
from matplotlib import pyplot

ix = 0
for groupname in groups.keys():
    temperatures = groups[groupname]
    name = NAMES[groupname]

    pyplot.style.use('ggplot')
    (n, bins, patches) = pyplot.hist(
        temperatures, BINS,
        label = 'Pitch temperatures for ' + name,
        range = (lowest, highest)
    )
    pyplot.title('Pitch temperatures for ' + name)
    pyplot.xlabel('Degrees C')
    pyplot.ylabel('Number of accounts')

    pyplot.savefig('pitch-%s.png' % ix)
    ix += 1
    pyplot.close()

# --- Combine

import imglib
imglib.tile_images(
    imagelist = [('pitch-%s.png' % i) for i in range(ix)],
    rows = [[0, 1]],
    outfile = 'pitch-temperature-histogram-by-harvest.png'
)
