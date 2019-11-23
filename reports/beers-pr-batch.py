
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

  ?s tb:beers-pr-batch ?h.

  ?c a dbp:Country.
}'''

tablelib.make_table('beers-pr-batch.html', query, str,
                    label = 'beers_pr_batch',
                    caption = 'Number of beers pr batch',
                    format = format)
