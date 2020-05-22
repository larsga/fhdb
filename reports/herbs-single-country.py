
import sys
import sparqllib
import tablelib

import herbs

format = tablelib.get_format()
country = sys.argv[2]

MIN_ACCOUNTS = 3

# ===== HERBS FOR ONE COUNTRY

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?h ?s
WHERE {
  ?s dc:title ?title;
    tb:part-of ?c;
    tb:herbs ?h.

  ?c a dbp:Country.
  FILTER( ?c = dbp:%s )
}''' % country
#  FILTER (?h != neg:alder-branches && ?h != neg:straw )

rows = [(herb, account) for (herb, account) in sparqllib.query_for_rows(query)]
accounts = set([account for (herb, account) in rows])

herb_count = {}
for (herb, account) in rows:
    herb_count[herb] = herb_count.get(herb, 0) + 1

herb_rows = herb_count.items()
herb_rows.sort(key = lambda pair: pair[1] * -1)

filename = 'herbs-single-country.html'

if format == 'html':
    writer = tablelib.HtmlWriter(open(filename, 'w'))
else:
    writer = tablelib.LatexWriter(
        open(filename, 'w'),
        label = 'tbl-herbs',
        caption = 'Herb usage.',
        columns = 3
    )


writer.start_table()
writer.header_row('Herb', 'Accounts', 'Percent')

for (herb, count) in herb_rows:
    writer.row(
        herbs.get_herb_name(herb),
        count,
        '%s %%' % tablelib.percent(count, len(accounts))
    )

writer.header_row('Total', len(accounts), '100%')
writer.end_table()
