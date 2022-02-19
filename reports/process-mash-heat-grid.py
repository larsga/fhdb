
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

processes = proclib.load_process_dict()

categories = [
    proclib.Process.is_single_infusion,
    proclib.Process.is_multistep_infusion,
    proclib.Process.is_decoction,
    proclib.Process.is_circulation,
    proclib.Process.is_kettle_mash,
    proclib.Process.is_mash_boiled,
    proclib.Process.is_stone_mash
]

catnames = {'en': [
    'Single-infusion',
    'Step mash',
    'Decoction',
    'Circulation',
    'Kettle heated',
    'Mash boiled',
    'Stones',
],
            'no' : [
    'Infusjon',
    'Stegmesking',
    'Dekoksjon',
    'Sirkulering',
    'Kjelevarming',
    'Mesk kokt',
    'Steiner',
],
}[args.lang]

FILTER = ''
if args.country:
    FILTER = '?s tb:part-of dbp:' + args.country

pairslist = []
query = '''
prefix dbp: <http://dbpedia.org/resource/>
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT ?s ?lat ?lng ?proc ?title ?procname
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:process ?proc.

  ?proc rdfs:label ?procname.
  %s
}''' % FILTER
for (s, lat, lng, proc, title, procname) in sparqllib.query_for_rows(query):
    proc = processes[proc]
    if not proc.is_mashing_fully_defined():
        continue

    matches = [ix for (ix, predicate) in enumerate(categories)
               if predicate(proc)]

    if len(matches) == 1:
        pairs = [(matches[0], matches[0])]
        if matches[0] == 3:
            print(proc.get_no(), procname, title)
    else:
        pairs = []
        for ix in range(len(matches)):
            for ix2 in range(ix+1, len(matches)):
                pairs.append((matches[ix], matches[ix2]))

    if args.debug:
        print(proc.get_no(), procname, pairs)

    if not pairs:
        continue # probably oven-based

    pairslist.append(pairs)

grid = [[0] * len(categories) for ix in range(len(categories))]
for pairs in pairslist:
    fraction = 1.0 #/ max(1, len(pairs) - 1)

    for (ix, ix2) in pairs:
        grid[ix][ix2] += fraction
        if ix != ix2:
            grid[ix2][ix] += fraction

themax = max([max(row) for row in grid])

# ===== DISPLAY

import matplotlib
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
im = ax.imshow(grid)

# Show all ticks and label them with the respective list entries
ax.set_xticks(range(len(catnames)), labels=catnames)
ax.set_yticks(range(len(catnames)), labels=catnames)

# Rotate the tick labels and set their alignment.
plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
         rotation_mode="anchor")

# Loop over data dimensions and create text annotations.
for i in range(len(catnames)):
    for j in range(len(catnames)):
        text = ax.text(j, i, int(round(grid[i][j] + 0.01)),
                       ha="center", va="center", color="w")

ax.set_title({
    'en' : 'Combinations of mashing techniques',
    'no' : 'Kombinasjoner av meskemetoder',
}[args.lang])
fig.tight_layout()
if args.file:
    plt.savefig(args.file)
else:
    plt.show()
