
import sparqllib
import maputils, tablelib

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?s ?title ?h ?lat ?lng
WHERE {
  ?s dc:title ?title;
    tb:malt-drying-wood ?h;
    geo:lat ?lat;
    geo:long ?lng.
}'''

symbols = {
    ('http://www.garshol.priv.no/2014/neg/juniper', '#00FF00', 'juniper'),
    ('http://www.garshol.priv.no/2014/neg/alder',   '#FF0000', 'alder'),
    ('http://www.garshol.priv.no/2014/neg/birch',   '#FFFFFF', 'birch'),
    ('http://www.garshol.priv.no/2014/neg/beech',   '#88CC88', 'beech'),
    ('http://www.garshol.priv.no/2014/neg/peat',    '#eb9a49', 'peat'),
    # ('http://www.garshol.priv.no/2014/neg/ash',     '#000000', 'ash'),
    # ('http://www.garshol.priv.no/2014/neg/willow',  '#000000', 'willow'),
    # ('http://www.garshol.priv.no/2014/neg/mosetre', '#000000', 'mosetre'),
    # ('knasturr lauvved',                            '#000000', 'lauvved'),
    # ('http://www.garshol.priv.no/2014/neg/heather', '#000000', 'heather'),
    # ('http://www.garshol.priv.no/2014/neg/oak',     '#000000', 'oak'),
    # ('http://www.garshol.priv.no/2014/neg/spruce',  '#000000', 'spruce'),
    # ('http://www.garshol.priv.no/2014/neg/hazel',   '#000000', 'hazel'),
    # ('http://www.garshol.priv.no/2014/neg/hatleris','#000000', 'hatleris'),
}

maputils.make_thing_map(query, symbols, 'malt-drying-wood-map',
                        legend = True)
