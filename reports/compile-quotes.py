
import sys, codecs
import sparqllib

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?title ?quote
WHERE {
  ?s dc:title ?title;
    tb:%s-q ?quote.
}
'''

prop = sys.argv[1]

with codecs.open('compile-quotes.html', 'w', 'utf-8') as f:
    f.write('''
    <style>
      body {
        margin-left: 15%;
        margin-right: 15%;
      }
      p.quote {
        margin-bottom: 0;
      }
      p.cite {
        text-align: right;
        color: #777;
        margin-top: 0;
      }
    </style>
    ''')

    for (title, quote) in sparqllib.query_for_rows(query % prop):
        f.write(u'<p class=quote>%s</p>\n' % quote)
        f.write(u'<p class=cite>%s</p>\n' % title)
