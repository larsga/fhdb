
import sparqllib
import tablelib

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix dbp: <http://dbpedia.org/resource/>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT DISTINCT ?h ?c ?s
WHERE {
  ?s dc:title ?title;
    tb:part-of ?c.

  ?s tb:clean-with ?h.

  ?c a dbp:Country.
}'''

def get_herb_name(h):
    return tablelib.get_last_part(str(h))

tablelib.make_table('cleaning-table.html', query, get_herb_name,
                    label = 'cleaning',
                    caption = 'Accounts of cleaning methods by country',
                    format = 'html')
