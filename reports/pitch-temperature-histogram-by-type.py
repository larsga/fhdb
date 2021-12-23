#encoding=utf-8

import sparqllib
import pitch

BINS = 10

NEG = 'http://www.garshol.priv.no/2014/neg/'
GROUPS = {
    "Farmhouse yeast" : [NEG + 'own-yeast'],
    "Brewers' yeast" :  [NEG + 'brewers-yeast'],
    "Lager yeast'"   :  [NEG + 'lager-yeast'],
    "Bakers' yeast"  :  [NEG + 'bakers-yeast', NEG + 'distillers-yeast'],
}

def average(numbers):
    return sum(numbers) / len(numbers)

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?s ?lat ?lng ?t ?type
WHERE {
  ?s dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:pitch-temperature ?t;
    tb:yeast-type ?type.
}'''

groups = {}
for (s, lat, lng, t, group) in sparqllib.query_for_rows(query):
    temp = pitch.get_temp(t)

    if temp:
        if group not in groups:
            groups[group] = []
        groups[group].append(temp)

import numpy
from matplotlib import pyplot

ix = 0
for groupname in GROUPS.keys():
    temperatures = []
    for grpid in GROUPS[groupname]:
        temperatures += groups.get(grpid, [])

    #pyplot.style.use('grayscale')
    (n, bins, patches) = pyplot.hist(
        temperatures, BINS, alpha=0.5,
        label = 'Pitch temperatures for ' + groupname
    )
    pyplot.title('Pitch temperatures for ' + groupname)
    pyplot.xlabel('Degrees C')
    pyplot.ylabel('Number of accounts')

    pyplot.savefig('pitch-%s.png' % ix)
    ix += 1
    pyplot.close()

# --- Combine

import imglib

imglib.tile_images(
    imagelist = ['pitch-%s.png' % i for i in range(ix)],
    rows = [[0, 1], [2, 3]],
    outfile = 'pitch-temperature-histogram-by-type.png'
)
