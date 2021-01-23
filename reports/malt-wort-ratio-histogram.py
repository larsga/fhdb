
import sparqllib

BINS = 20

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix sproc: <http://www.garshol.priv.no/2014/trad-beer/simple-process/>

SELECT DISTINCT ?s ?malts
WHERE {
  ?s dc:title ?title;
    tb:malt-wort-ratio ?malts;
    geo:lat ?lat;
    geo:long ?lng;
}'''

  #   tb:process ?proc.
  # ?proc neg:variant-of ?sproc.
  # ?sproc neg:variant-of ?ssproc.
  # FILTER (?ssproc = sproc:complex-mash)

ratios = [float(ratio) for (s, ratio) in sparqllib.query_for_rows(query)]

from matplotlib import pyplot

#pyplot.style.use('grayscale')
(n, bins, patches) = pyplot.hist(ratios, BINS, alpha=0.5,
                                 label = 'Malt/wort ratios')
pyplot.title('Farmhouse ale strength')
pyplot.xlabel('Kilos of malt pr liter')
pyplot.ylabel('Number of accounts')
pyplot.show()
