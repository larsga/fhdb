
import tablelib

format = tablelib.get_format()

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix dbp: <http://dbpedia.org/resource/>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT DISTINCT ?h ?c ?s
WHERE {
  ?s dc:title ?title;
    tb:part-of ?c;
    tb:barley-rows ?h.

  ?c a dbp:Country.
}'''

def make_label(v):
    ix = v.rfind('/')
    if ix != -1:
        v = v[ix + 1 : ]
    return v + '-row'

tablelib.make_table('barley-rows.html', query, make_label,
                    'barley-types',
                    'Preferences for barley types',
                    format = format)
