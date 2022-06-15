
import argparse
import sparqllib
import tablelib

parser = argparse.ArgumentParser()
parser.add_argument('--lang', default = 'en')
parser.add_argument('--format', default = 'html')
parser.add_argument('--min', type=int, default = 1)
# <http://www.garshol.priv.no/2021/landsdel/Landsdel>
parser.add_argument('--regiontype', default = 'dbp:Country')
args = parser.parse_args()

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix dbp: <http://dbpedia.org/resource/>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT DISTINCT ?h ?c ?s
WHERE {
  ?s dc:title ?title;
    tb:part-of ?c.

  ?s tb:clean-with ?h.

  ?c a %s.
}''' % args.regiontype

def get_herb_name(h):
    return tablelib.get_last_part(str(h))

tablelib.make_table(
    'cleaning-table.html', query, get_herb_name,
    min_accounts = args.min,
    label = 'cleaning',
    caption = 'Accounts of cleaning methods by country',
    format = args.format,
    lang = args.lang,
)
