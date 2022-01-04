
import tablelib, sparqllib

MIN_ACCOUNTS = 1

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>

SELECT DISTINCT ?proc ?c ?s
WHERE {
  ?s
    dc:title ?title;
    tb:part-of ?c;
    tb:fermentor-wrap ?proc.

  ?c a dbp:Country.
}'''

q2 = '''
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

select ?s ?l where {
  ?s a tb:FermentorWrapping;
    rdfs:label ?l.
}
'''

labels = {uri : label for (uri, label) in sparqllib.query_for_rows(q2)}
def get_method_name(uri):
    if uri == 'Other':
        return 'Other'
    return labels[uri]

mapping = {
    # 'straw-ring-with-hops' : 'straw-ring',
    # 'straw'                : 'straw-ring',
    # 'cloth-over-ash'       : 'cloth',
    # 'trough'               : 'wooden-object',
    # 'trough-and-cloth'     : 'wooden-object',
    # 'wooden-boards'        : 'wooden-object',
    # 'plate'                : 'wooden-object',
    # 'bowl'                 : 'wooden-object',
}
# mapping = {YEAST + k : YEAST + v for (k, v) in mapping.items()}

tablelib.make_table(
    'fermentor-wrap-table.html', query, get_method_name,
    label = 'fermentor_wrap',
    caption = 'What fermentors are wrapped in',
    min_accounts = MIN_ACCOUNTS,
    format = tablelib.get_format(),
    country = tablelib.get_country(),
    simplify_mapping = mapping
)