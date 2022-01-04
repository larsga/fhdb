# encoding=utf-8

import config
import sparqllib
import tablelib
import proclib

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>

SELECT DISTINCT ?s ?lat ?lng ?proc ?title ?procname ?c
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:process ?proc;
    tb:part-of ?c.

  ?proc rdfs:label ?procname.
  ?c a dbp:Country.
}'''

process_categories = proclib.classify_main_heating()
table = tablelib.CountryTable(1)
for (s, lat, lng, proc, title, procname, c) in sparqllib.query_for_rows(query):

    cat = process_categories.get(proc)
    if cat == None:
        #print('UNMAPPED', repr(proc))
        continue

    table.add_account(cat, c, s)

out = tablelib.HtmlWriter(open('process-main-heat-table.html', 'w'))
#out = tablelib.TabWriter(sys.stdout, 'w')
tablelib.write_table(out, table, lambda v: v)
