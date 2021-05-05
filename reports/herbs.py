
import sparqllib
import tablelib

format = tablelib.get_format()
property = 'tb:herbs'

MIN_ACCOUNTS = 3

# merge herbs in the statistics without having to merge them in the
# source data. used for synonyms I have decided to accept, but means I
# can change my mind
NEG = 'http://www.garshol.priv.no/2014/neg/'
TRANSLATIONS = {
    NEG + 'grobone' : NEG + 'artemisia-vulgaris'
}

def better_than(repl, orig):
    if not orig:
        return True

    if repl.lang == 'en':
        return True

    return False

query = '''
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix dc: <http://purl.org/dc/terms/>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix owl: <http://www.w3.org/2002/07/owl#>

select * where {
  ?h a neg:Herb; rdfs:label ?l
}
'''
herb_names = {}
for (h, l) in sparqllib.sparql.query(sparqllib.ENDPOINT, query):
    h = sparqllib.value(h)

    n = herb_names.get(h)
    if better_than(l, n):
        herb_names[h] = l

herb_names = {url : sparqllib.value(label) for (url, label)
              in herb_names.items()}

# import pprint
# pprint.pprint(herb_names)
# import sys; sys.exit(0)

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
    %s ?h.

  ?c a dbp:Country.
}''' % property
#  FILTER (?h != neg:alder-branches && ?h != neg:straw )

def get_herb_name(h):
    return herb_names.get(str(h), tablelib.get_last_part(str(h)))

CAPTION = '''Herbs used in farmhouse brewing. Columns are not exclusive. Every herb mentioned in the source is included, even if the source says only 'I have heard' or 'I think it was used'.'''

if __name__ == '__main__':
    tablelib.make_table('herbs.html', query, get_herb_name,
                        label = 'herbs',
                        caption = CAPTION,
                        min_accounts = MIN_ACCOUNTS,
                        format = format)

# # ===== HERBS BY PROVINCE

# query = '''
# prefix dc: <http://purl.org/dc/elements/1.1/>
# prefix neg: <http://www.garshol.priv.no/2014/neg/>
# prefix neu: <http://www.garshol.priv.no/2015/neu/>
# prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
# prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
# prefix dbp: <http://dbpedia.org/resource/>
# prefix uff: <http://www.garshol.priv.no/2015/uff/>

# SELECT DISTINCT ?h ?c ?p ?s
# WHERE {
#   ?s dc:title ?title;
#     tb:herbs ?h.

#   { ?s tb:part-of ?p }
#   UNION
#   { ?s neg:fylke ?p }

#   ?p a dbp:Province; tb:part-of ?c.
#   ?c a dbp:Country.
#   FILTER (?h != neg:alder-branches && ?h != neg:straw && ?h != neg:alder-barch)
# }'''

# all_herbs = set()
# herbs = {} # h, p -> set(...)
# provinces = {} # p -> set(s1, s2, s3, ...)
# countries = {} # p -> c

# for (h, c, p, s) in sparqllib.query_for_rows(query):
#     # province-count
#     if p not in provinces:
#         provinces[p] = set()

#     provinces[p].add(s)

#     # herb percentage
#     if (h, p) not in herbs:
#         herbs[(h, p)] = set()

#     herbs[(h, p)].add(s)

#     # all herbs
#     all_herbs.add(h)

#     countries[p] = c

# # simplify calculations by rewriting the sets to numbers
# provinces = {p : len(rs) for (p, rs) in provinces.items()}
# herbs = {(h, p) : len(rs) for ((h, p), rs) in herbs.items()}

# # sort the herbs by frequency of use
# herb_total = {h : sum([herbs.get((h, p), 0) for p in provinces.keys()])
#               for h in all_herbs}
# all_herbs = list(all_herbs)
# all_herbs.sort(key = lambda h: -herb_total[h])

# # ditch little-used herbs
# for (ix, h) in enumerate(all_herbs):
#     if herb_total[h] < 2:
#         break
# all_herbs = all_herbs[ : ix]

# writer = tablelib.HtmlWriter(open('herbs-by-province.html', 'w'))
# tablelib.write_table(writer, provinces, all_herbs, herbs,
#                      get_herb_name)
