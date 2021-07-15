
import tablelib

format = tablelib.get_format()

MIN_ACCOUNTS = 1

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix skos: <http://www.w3.org/2008/05/skos#>

SELECT DISTINCT ?h ?c ?s
WHERE {
  ?s dc:title ?title;
    tb:part-of ?c;
    tb:strainer ?h.

  ?c a dbp:Country.
  ?h skos:broader neg:straw.
}'''
#  FILTER (?h != neg:alder-branches && ?h != neg:straw )

if __name__ == '__main__':
    tablelib.make_table('straw-filter-table.html',
                        query, tablelib.get_last_part,
                        label = 'straw_filter',
                        caption = '',
                        min_accounts = MIN_ACCOUNTS,
                        format = format)
