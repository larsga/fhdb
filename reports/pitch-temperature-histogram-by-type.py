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

from PIL import Image

images = [Image.open('pitch-%s.png' % i) for i in range(ix)]
widths, heights = zip(*(i.size for i in images))

width = max(widths) * 2
height = heights[0] + heights[1]

new_im = Image.new('RGB', (width, height))

y_offset = 0
for im in images[ : 2]:
  new_im.paste(im, (0, y_offset))
  y_offset += im.size[1]

y_offset = 0
for im in images[2 : ]:
  new_im.paste(im, (images[0].size[0], y_offset))
  y_offset += im.size[1]

new_im.save('pitch-temperature-histogram-by-type.png')

import sys, os
if len(sys.argv) > 1:
    os.system('open pitch-temperature-histogram-by-type.png')
