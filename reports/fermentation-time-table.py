
import sparqllib, tablelib

# DATABASE IN GENERAL
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
    tb:fermentation-time ?h.

  ?c a dbp:Country.
}

''' #   FILTER (?c = dbp:Norway)

def sort_columns(cols):
    cols.sort()
    return cols

def column_label(pair):
    return '%s-%s' % pair

def to_pair(v):
    min = v - (v % INTERVAL_SIZE)
    return (int(min), int(min + INTERVAL_SIZE))

INTERVAL_SIZE = 25
MAX = 300
columns = [
    (ix * INTERVAL_SIZE, (ix+1) * INTERVAL_SIZE)
    for ix in range(MAX / INTERVAL_SIZE)
]

table = tablelib.CountryTable(1, sort_columns = sort_columns)

for (t, c, s) in sparqllib.query_for_rows(query):
    time = float(t)
    bracket = to_pair(time)
    table.add_account(bracket, c, s)


out = tablelib.HtmlWriter(open('fermentation-time-table.html', 'w'))
#out = tablelib.TabWriter(sys.stdout, 'w')
tablelib.write_table(out, table, column_label)
