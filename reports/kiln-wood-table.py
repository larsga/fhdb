
import sys, os
import sparqllib
import tablelib

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?s ?dry ?wood
WHERE {
  ?s dc:title ?title;
    tb:malt-drying ?dry;
    tb:malt-drying-wood ?wood.
}'''

def get_name(h):
    return tablelib.get_last_part(str(h))

MALT = 'http://www.garshol.priv.no/2014/trad-beer/malt-drying/'
simplify = {
    MALT + 'a-shaped-kiln' : MALT + 'soinn',
}

filename = 'kiln-wood-table.html'
table = tablelib.CountryTable(min_accounts = 1)

for (s, dry, wood) in sparqllib.query_for_rows(query):
    dry = simplify.get(dry, dry)
    table.add_account(wood, dry, s)

writer = tablelib.HtmlWriter(open(filename, 'w'))
tablelib.write_table(writer, table, get_name)

if len(sys.argv) > 1:
    os.system('open %s' % filename)
