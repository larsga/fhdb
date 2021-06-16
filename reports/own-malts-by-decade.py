
import sparqllib
import tablelib

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix dbp: <http://dbpedia.org/resource/>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT DISTINCT ?s ?year ?yeast
WHERE {
  ?s dc:title ?title;
    tb:year ?year.

  ?s tb:own-malts ?yeast.
}'''

def decade(year):
    return (int(year) / 10) * 10

def bicade(year):
    bic = int(year) / 10
    bic = bic - (bic % 2)
    return bic * 10

def label(v):
    if v == 'http://www.garshol.priv.no/2014/neg/borderline':
        return 'borderline'
    elif v == 'true':
        return 'Own malts'
    else:
        return 'Bought malts'

def sort_rows():
    rows = list(set(table._country.values()))
    rows.sort()
    return rows

table = tablelib.CountryTable(0, sort_rows = sort_rows, row_label = 'Decade')

for (s, year, yeast) in sparqllib.query_for_rows(query):
    table.add_account(yeast, decade(year), s)

writer = tablelib.HtmlWriter(open('own-malts-by-decade.html', 'w'))
tablelib.write_table(writer, table, label)
