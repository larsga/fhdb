
import sparqllib
import tablelib

country = 'Norway'
format = 'latex'
LANG = 'no'

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix dbp: <http://dbpedia.org/resource/>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT DISTINCT ?s ?h
WHERE {
  ?s dc:title ?title;
    tb:part-of ?c.

  { ?s tb:grain ?h. }
  UNION
  { ?s tb:secondary-grain ?h. }

  FILTER( ?c = dbp:%s )
}''' % country

NEG = 'http://www.garshol.priv.no/2014/neg/'
labels = {'no' : {
    NEG + 'barley' : 'bygg',
    NEG + 'rye' : 'rug',
    NEG + 'oats' : 'havre',
    }
}

headers = {
    'no' : ['Sort', 'Beskrivelser', 'Prosent'],
    'en' : ['Grain', 'Accounts', 'Percentage']
}

accounts = set()
grains = {}
for (url, grain) in sparqllib.query_for_rows(query):
    accounts.add(url)
    grains[grain] = grains.get(grain, 0) + 1

outf = open('grain-table-country.tex', 'w')
tab = tablelib.LatexWriter(outf, 'tbl-grain-table-country', '''
Antall kilder som oppgir bruk av ulike kornsorter til malt.
Summerer til mer enn 100% fordi mange brukte mer enn en kornsort.
''', 3)
tab.start_table()
tab.header_row(headers[LANG][0], headers[LANG][1], headers[LANG][2])

for (grain, count) in grains.items():
    p = round(float(count) / len(accounts) * 1000) / 10.0
    tab.row(labels[LANG][grain], count, p)

tab.end_table()
outf.close()
