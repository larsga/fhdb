
import tablelib

format = tablelib.get_format()

label = {
    'http://www.garshol.priv.no/2014/neg/top' : 'Top',
    'http://www.garshol.priv.no/2014/neg/bottom' : 'Bottom',
    'http://www.garshol.priv.no/2014/neg/cask-bottom' : 'Cask bottom',
    'http://www.garshol.priv.no/2014/neg/both' : 'Both',
    'http://www.garshol.priv.no/2014/neg/either' : 'Either',
}

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix eu: <http://www.garshol.priv.no/2017/eu/>
prefix r: <http://www.garshol.priv.no/2014/trad-beer/recipe/>
prefix dbp: <http://dbpedia.org/resource/>

SELECT DISTINCT ?harvest ?c ?s
WHERE {
  ?s
    dc:title ?title;
    tb:part-of ?c;
    tb:yeast-harvest ?harvest.
  ?c a dbp:Country.
}'''
tablelib.make_table('yeast-harvest-table.html', query, lambda u: label[u],
                    label = 'yeast-harvest',
                    caption = 'Yeast harvest',
                    min_accounts = 1,
                    format = format)
