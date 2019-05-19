
import sparqllib

names = {
    'http://www.garshol.priv.no/2014/trad-beer/Recipe' : 'Own collection',
    'http://www.garshol.priv.no/2015/luf/Response' : 'LUF',
    'http://www.garshol.priv.no/2015/sls/Response' : 'SLS',
    'http://www.garshol.priv.no/2014/neg/Response' : 'NEG',
    'http://www.garshol.priv.no/2015/uff/Communication' : 'AFD',
    'http://www.garshol.priv.no/2016/voko/Manuskript' : 'VOKO',
    'http://www.garshol.priv.no/2015/neu/Item' : 'NEU',
    'http://www.garshol.priv.no/2016/km/Account' : 'KM',
    'http://www.garshol.priv.no/2016/dot/DataPoint' : 'DOTS',
    'http://www.garshol.priv.no/2017/eu/Response': 'EU',
    'http://www.garshol.priv.no/2017/eu/HopResponse' : 'EU SP98',
    'http://www.garshol.priv.no/2018/sm/Account' : 'SM',
    'http://www.garshol.priv.no/2018/ulma/Account' : 'ULMA',
    'http://www.garshol.priv.no/2019/erm/Account' : 'ERM',
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
    for (typeurl, name) in names.items()
}


# pages by type
query = '''
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
select ?t sum(?p) where {
  ?s tb:page-count ?p; a ?t
} group by ?t
'''
pages = {url : pages for (url, pages) in sparqllib.query_for_rows(query)}

# accounts by type
query = '''
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
select ?t count(?s) where {
  ?t rdfs:subClassOf tb:Account.
  ?s a ?t.
} group by ?t
'''

total = 0
ptotal = 0
ttotal = 0
rows = list(sparqllib.query_for_rows(query))

biggest = reduce(max, [len(name) for name in names.values()])

TEMPLATE = '%20s   %4s   %4s   %5s'
print TEMPLATE % ('Dataset', 'Accts', 'Pages', 'Triples')
for (t, c) in rows:
    name = names[t]
    name = name + (' ' * (biggest + 2 - len(name)))

    print TEMPLATE % \
        (name, c, pages.get(t, ''), triples.get(t, ''))
    total += int(c)
    ptotal += int(pages.get(t, 0))
    ttotal += int(triples.get(t, 0))

print TEMPLATE % ('TOTAL', total, ptotal, ttotal)
