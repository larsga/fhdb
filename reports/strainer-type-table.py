
import tablelib

format = tablelib.get_format()

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix dbp: <http://dbpedia.org/resource/>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT DISTINCT ?st ?c ?s
WHERE {
  ?s dc:title ?title;
    tb:part-of ?c.

  ?s tb:strainer-type ?st.

  ?c a dbp:Country.
}'''

tablelib.make_table('strainer-type-table.html', query,
                    tablelib.get_last_part,
                    label = 'strainertypes',
                    caption = 'Strainer types used by country',
                    format = format)
