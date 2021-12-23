
import sparqllib
import tablelib

# ===== EVENTS BY COUNTRY

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
    tb:brew-for ?h.

  ?c a dbp:Country.
}'''
#  FILTER (?h != neg:alder-branches && ?h != neg:straw )

def get_herb_name(h):
    return tablelib.get_last_part(str(h))

tablelib.make_table('brew-for.html', query, get_herb_name,
                    label = 'events',
                    caption = 'Brewing for annual events.',
                    min_accounts = 8,
                    format = 'html')
