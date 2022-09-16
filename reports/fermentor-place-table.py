
import tablelib, sparqllib, utils

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--lang', default = 'en')
parser.add_argument('--country')
parser.add_argument('--format', default = 'html')
parser.add_argument('--min', type=int, default = 2)
args = parser.parse_args()

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>

SELECT DISTINCT ?proc ?c ?s
WHERE {
  ?s
    dc:title ?title;
    tb:part-of ?c;
    tb:fermentor-place ?proc.

  ?c a dbp:Country.
}'''

q2 = '''
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

select ?s ?l where {
  ?s a tb:FermentorLocation;
    rdfs:label ?l.
}
'''

labels = utils.collect_labels(q2, args.lang)
def get_method_name(uri):
    if uri in ('Other', 'Annet'):
        return uri
    return labels[uri]

mapping = {
    # 'straw-ring-with-hops' : 'straw-ring',
}
mapping = {YEAST + k : YEAST + v for (k, v) in mapping.items()}

tablelib.make_table(
    'fermentor-place-table.html', query, get_method_name,
    label = 'fermentor_place',
    caption = 'Where fermentors were traditionally placed during fermentation',
    min_accounts = args.min,
    format = args.format,
    country = args.country,
    simplify_mapping = mapping,
    lang = args.lang
)
