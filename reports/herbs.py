
import argparse
import sparqllib
import tablelib
import utils

parser = argparse.ArgumentParser()
parser.add_argument('--lang', default = 'en')
parser.add_argument('--format', default = 'html')
parser.add_argument('--recipe', action='store_true')
parser.add_argument('--min', type=int, default = 4)
# <http://www.garshol.priv.no/2021/landsdel/Landsdel>
parser.add_argument('--regiontype', default = 'dbp:Country')
args = parser.parse_args()

format = args.format
property = 'tb:herbs' if not args.recipe else 'tb:recipe-herbs'
region_type = args.regiontype
LANG = args.lang
MIN_ACCOUNTS = args.min

# merge herbs in the statistics without having to merge them in the
# source data. used for synonyms I have decided to accept, but means I
# can change my mind
NEG = 'http://www.garshol.priv.no/2014/neg/'
TRANSLATIONS = {
    NEG + 'grobone' : NEG + 'artemisia-vulgaris'
}

# ===== HERBS BY COUNTRY

PREFIXES = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
'''

query = PREFIXES + '''
select ?c ?l where {
  ?c a %s; rdfs:label ?l
}
''' % region_type
region_labels = utils.collect_labels(query, LANG)

query = PREFIXES + '''
select ?h ?l where {
  ?h a neg:Herb; rdfs:label ?l
}
'''
herb_names = utils.collect_labels(query, LANG)

query = PREFIXES + '''
SELECT DISTINCT ?h ?c ?s
WHERE {
  ?s dc:title ?title;
    tb:part-of ?c;
    %s ?h.

  ?c a %s.
}''' % (property, region_type)
#  FILTER (?h != neg:alder-branches && ?h != neg:straw )

def get_herb_name(h):
    return herb_names.get(str(h), tablelib.get_last_part(str(h)))

def get_region_name(url):
    return region_labels[url]

q = PREFIXES + 'select <http://whoops> ?label where { %s rdfs:label ?label }' % region_type
regiontype_name = utils.collect_labels(q, LANG)['http://whoops']

CAPTION = '''Herbs used in farmhouse brewing. Columns are not exclusive. Every herb mentioned in the source is included, even if the source says only 'I have heard' or 'I think it was used'.'''

if __name__ == '__main__':
    tablelib.make_table(
        'herbs', query, get_herb_name,
        label = 'herbs',
        caption = CAPTION,
        min_accounts = MIN_ACCOUNTS,
        get_row_label = get_region_name,
        row_type_name = regiontype_name,
        format = format,
        lang = LANG
    )

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
