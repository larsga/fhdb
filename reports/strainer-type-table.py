
import argparse
import tablelib, config

parser = argparse.ArgumentParser()
parser.add_argument('--lang', default = 'en')
parser.add_argument('--format', default = 'html')
parser.add_argument('--min', type=int, default = 4)
# <http://www.garshol.priv.no/2021/landsdel/Landsdel>
parser.add_argument('--regiontype', default = 'dbp:Country')
args = parser.parse_args()

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

  ?c a %s.
}''' % args.regiontype

tablelib.make_table('strainer-type-table', query,
                    tablelib.get_last_part,
                    label = 'strainertypes',
                    caption = 'Strainer types used by country',
                    format = args.format)
