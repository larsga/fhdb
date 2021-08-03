
import sparqllib
import tablelib

format = tablelib.get_format()

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?w ?c ?s
WHERE {
  ?s dc:title ?title;
    tb:part-of ?c;
    tb:fermentor-wrap ?w.

  ?c a dbp:Country.
}'''

def column_label(wrap):
    if wrap:
        return 'Insulated'
    else:
        return 'Not insulated'

NEG_NONE = 'http://www.garshol.priv.no/2014/neg/none'

table = tablelib.CountryTable(1)
count = 0
for (wrap, country, url) in sparqllib.query_for_rows(query):
    insulated = wrap != NEG_NONE
    table.add_account(insulated, country, url)

out = tablelib.HtmlWriter(open('fermentor-heat-table.html', 'w'))
tablelib.write_table(out, table, column_label)
