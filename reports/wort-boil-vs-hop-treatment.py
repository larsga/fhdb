# encoding=utf-8

import argparse
import sparqllib
import proclib

parser = argparse.ArgumentParser()
parser.add_argument('--country')
parser.add_argument('--file')
parser.add_argument('--lang', default='en')
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()

# ===== STARTING

labels = {'en': {
    'true' : 'Boiled',
    'false' : 'Not boiled',
    'http://www.garshol.priv.no/2014/neg/borderline' : 'Borderline',
    'hoptreats' : ['Boiled in wort', 'Humlebeit', 'Hop tea', 'Hops in mash',
                   'Boiled in mash', 'Dry hopping', 'Lauter through hops'],
},
          'no' : {
    'true' : 'Kokt',
    'false' : 'Ikke kokt',
    'http://www.garshol.priv.no/2014/neg/borderline' : 'Oppkok',
    'hoptreats' : [u'Kokt i vørter', 'Humlebeit', 'Humle-te', 'Humle i mesk',
                   'Humle kokt i mesk', u'Tørrhumling', 'Renn gjennom humle'],
},
}[args.lang]

FILTER = ''
if args.country:
    FILTER = '?s tb:part-of dbp:' + args.country

TB = 'http://www.garshol.priv.no/2014/trad-beer/'
wortboils = ['true', 'http://www.garshol.priv.no/2014/neg/borderline', 'false']
hoptreats = [TB + ht for ht in [
    'boil-hops-in-wort', 'humlebeit', 'hop-tea', 'hops-in-mash',
    'boil-hops-in-mash', 'dry-hopping', 'lauter-through-hops',
]]

grid = [[0] * len(wortboils) for ix in range(len(hoptreats))]

query = '''
prefix dbp: <http://dbpedia.org/resource/>
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT ?s ?lat ?lng ?proc ?boil ?treat
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:process ?proc.

  ?proc rdfs:label ?procname;
    tb:wort-boiled ?boil;
    tb:hop-treatment ?treat.
  %s
}''' % FILTER
for (s, lat, lng, proc, boil, treat) in sparqllib.query_for_rows(query):
    ix = hoptreats.index(treat)
    ix2 = wortboils.index(boil)
    grid[ix][ix2] += 1

themax = max([max(row) for row in grid])

# ===== DISPLAY

def tolabel(uri):
    ix = uri.rfind('/')
    return uri[ix + 1 : ].replace('-', ' ')

import matplotlib
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
im = ax.imshow(grid)

# Show all ticks and label them with the respective list entries
ax.set_yticks(range(len(hoptreats)), labels=labels['hoptreats'])
ax.set_xticks(range(len(wortboils)), labels=[labels[wb] for wb in wortboils])

# Rotate the tick labels and set their alignment.
plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
         rotation_mode="anchor")

# Loop over data dimensions and create text annotations.
for i in range(len(hoptreats)):
    for j in range(len(wortboils)):
        text = ax.text(j, i, grid[i][j],
                       ha="center", va="center", color="w")

ax.set_title({
    'en' : 'Wort boil vs hop treatment',
    'no' : 'Vørterkok mot humlebehandling',
}[args.lang])
fig.tight_layout()
if args.file:
    plt.savefig(args.file)
else:
    plt.show()
