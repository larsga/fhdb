
import sparqllib
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
    tb:part-of ?c.

  { ?s tb:grain ?h. }
  UNION
  { ?s tb:secondary-grain ?h. }

  ?c a dbp:Country.
}'''

def get_herb_name(h):
    return tablelib.get_last_part(str(h))

tablelib.make_table('grain-table.html', query, get_herb_name,
                    label = 'graintypes',
                    caption = 'Accounts of grain type use by country',
                    format = format)
