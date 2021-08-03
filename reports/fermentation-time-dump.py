import codecs
import sparqllib, tablelib

# FIXME: get rid of duplicate years

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?s ?title ?h ?lat ?lng ?yeast ?year ?g ?country
WHERE {
  ?s dc:title ?title;
    tb:part-of ?country.
  ?country a dbp:Country.

  graph ?g {
    ?s tb:fermentation-time ?h.
  }

  OPTIONAL { ?s geo:lat ?lat; geo:long ?lng }
  OPTIONAL { ?s tb:yeast-type ?yeast }
  OPTIONAL { ?s tb:year ?year }
} order by ?title
''' #   FILTER (?c = dbp:Norway)


out = tablelib.HtmlWriter(codecs.open('fermentation-time-dump.html', 'w', 'utf-8'))

seen = set()

def none_to_empty(v):
    if v == None:
        return ''
    return v

def strip_uri(uri):
    ix = uri.rfind('/')
    return uri[ix + 1 : ]

by_graph = {}

rows = 0
out.start_table()
for (s, title, t, lat, lng, yeast, year, g, country) in sparqllib.query_for_rows(query):
    # if strip_uri(country) != 'Finland':
    #     continue

    rows += 1
    time = float(t)

    if yeast == None:
        yeast = ''
    else:
        yeast = strip_uri(yeast)

    out.row(title, time, none_to_empty(lat), none_to_empty(lng), yeast,
            none_to_empty(year), strip_uri(country))

    if s in seen:
        print 'DUPLICATE', s
    seen.add(s)

    by_graph[g] = by_graph.get(g, 0) + 1

out.end_table()
print 'ROWS:', rows

for (g, c) in by_graph.items():
    print g, c
