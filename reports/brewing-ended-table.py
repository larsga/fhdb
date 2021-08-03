
import sparqllib
import tablelib

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix dbp: <http://dbpedia.org/resource/>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT DISTINCT ?s ?year ?alive ?c
WHERE {
  ?s dc:title ?title;
    tb:part-of ?c;
    tb:year ?year.

  ?s tb:brewing-ended ?alive.
  ?c a dbp:Country.
}'''

def decade(year):
    return (int(year) / 10) * 10

def bicade(year):
    bic = int(year) / 10
    bic = bic - (bic % 2)
    return bic * 10

def label(v):
    return str(v)

def sort_columns(cols):
    cols.sort()
    return cols

table = tablelib.CountryTable(
    0,
    sort_columns = sort_columns
    # row_label = 'Decade'
)

decades = [y * 10 for y in range(185, 202)]
for (s, year, alive, country) in sparqllib.query_for_rows(query):
    d = decade(year)
    for dix in decades:
        if dix > d:
            break
        table.add_account(dix, country, s)

writer = tablelib.HtmlWriter(open('brewing-ended-table.html', 'w'))
tablelib.write_table(writer, table, label)
