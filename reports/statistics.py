
import sys
import sparqllib, tablelib

names = {
    'http://www.garshol.priv.no/2014/trad-beer/Recipe' : 'Own collection',
    'http://www.garshol.priv.no/2015/luf/Response' : 'LUF',
    'http://www.garshol.priv.no/2015/sls/Response' : 'SLS',
    'http://www.garshol.priv.no/2014/neg/Response' : 'NEG 35',
    'http://www.garshol.priv.no/2015/uff/Communication' : 'AFD',
    'http://www.garshol.priv.no/2016/voko/Manuskript' : 'VOKO',
    'http://www.garshol.priv.no/2015/neu/Item' : 'NEU',
    'http://www.garshol.priv.no/2016/km/Account' : 'KM',
    'http://www.garshol.priv.no/2016/dot/DataPoint' : 'DOTS',
    'http://www.garshol.priv.no/2017/eu/Response': 'EU',
    'http://www.garshol.priv.no/2017/eu/PseudoResponse': None,
    'http://www.garshol.priv.no/2017/eu/HopResponse' : 'EU SP98',
    'http://www.garshol.priv.no/2018/sm/Account' : 'SM',
    'http://www.garshol.priv.no/2018/ulma/Account' : 'ULMA',
    'http://www.garshol.priv.no/2019/erm/Account' : 'ERM',
    'http://www.garshol.priv.no/2019/erm/PseudoAccount': None,
    'http://www.garshol.priv.no/2014/neg/DrinkResponse' : 'NEG 28',
    'http://www.garshol.priv.no/2014/neg/SaunaResponse' : 'NEG 60',
}

# triples by type
query = '''
select count(*) where {
  graph ?g {
    ?s a <%s>; ?p ?o
  }
}
'''
triples = {
  typeurl : sparqllib.query_for_value(query % typeurl)
    for (typeurl, name) in names.items() if name
}


# pages by type
query = '''
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
select ?t sum(?p) where {
  ?s tb:page-count ?p; a ?t
} group by ?t
'''
pages = {url : pcount for (url, pcount) in sparqllib.query_for_rows(query)}

# accounts by type
query = '''
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
select ?t count(?s) where {
  select distinct ?t ?s where {
    ?t rdfs:subClassOf* tb:Account.
    ?s a ?t.
  }
} group by ?t
'''

total = 0
ptotal = 0
ttotal = 0
rows = list(sparqllib.query_for_rows(query))

biggest = reduce(max, [len(name) for name in names.values() if name])

rows = [(names[t], c, pages.get(t, ''), triples.get(t, ''))
    for (t, c) in rows if names[t]
]
rows.sort()

import tablelib

writer = tablelib.ConsoleWriter(sys.stdout)
#writer = tablelib.HtmlWriter(sys.stdout)
writer.start_table()

writer.header_row('Dataset', 'Accts', 'Pages', 'Triples')

for (name, count, pages, triples) in rows:
    name = name + (' ' * (biggest + 2 - len(name)))
    writer.row(name, count, pages, triples)
    total += int(count)
    ptotal += int(pages or 0)
    ttotal += int(triples or 0)

writer.row('TOTAL', total, ptotal, ttotal)
writer.end_table()
