
import sparqllib
import tablelib

query = '''
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

select * where {
  ?s tb:adjuncts ?a
}
'''

# ===== HERBS BY COUNTRY

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?h ?c ?s
WHERE {
  ?s dc:title ?title;
    tb:part-of ?c;
    tb:adjuncts ?h.

  ?c a dbp:Country.
}'''

table = tablelib.CountryTable(min_accounts = 2)
for (a, c, s) in sparqllib.query_for_rows(query):
    table.add_account(a, c, s)

out = tablelib.HtmlWriter(open('adjunct-table.html', 'w'))
tablelib.write_table(out, table, tablelib.get_last_part)
