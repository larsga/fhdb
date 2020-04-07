
import sparqllib
import tablelib

format = tablelib.get_format()

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
    tb:malt-drying-wood ?h.

  ?c a dbp:Country.
}'''

def get_wood_name(h):
    return tablelib.get_last_part(str(h))

tablelib.make_table('malt-drying-wood.html', query, get_wood_name,
                    label = 'malt-drying-wood',
                    caption = 'Fuels used to dry malts. Sometimes more than one choice per account, so rows do not sum to 100\%.',
                    min_accounts = 1,
                    format = format)
