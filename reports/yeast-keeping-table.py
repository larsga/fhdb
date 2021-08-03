
import tablelib, sparqllib

MIN_ACCOUNTS = 2

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix yeast: <http://www.garshol.priv.no/2017/trad-beer/yeast-keeping/>
prefix dbp: <http://dbpedia.org/resource/>

SELECT DISTINCT ?proc ?c ?s
WHERE {
  ?s
    dc:title ?title;
    tb:part-of ?c;
    tb:yeast-keeping ?proc.

  ?c a dbp:Country.
}'''

q2 = '''
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix yeast: <http://www.garshol.priv.no/2017/trad-beer/yeast-keeping/>

select ?s ?l where {
  ?s a tb:YeastKeepingMethod;
    rdfs:label ?l.
}
'''

labels = {uri : label for (uri, label) in sparqllib.query_for_rows(q2)}
def get_method_name(uri):
    if uri == 'Other':
        return 'Other'
    return labels[uri]

YEAST = 'http://www.garshol.priv.no/2017/trad-beer/yeast-keeping/'
mapping = {
    'straw-ring-with-hops' : 'straw-ring',
    'straw'                : 'straw-ring',
    'cloth-over-ash'       : 'cloth',
    'trough'               : 'wooden-object',
    'trough-and-cloth'     : 'wooden-object',
    'wooden-boards'        : 'wooden-object',
    'plate'                : 'wooden-object',
    'bowl'                 : 'wooden-object',
}
mapping = {YEAST + k : YEAST + v for (k, v) in mapping.items()}

tablelib.make_table(
    'yeast-keeping-table.html', query, get_method_name,
    label = 'yeast_keeping',
    caption = 'Methods for yeast preservation',
    min_accounts = MIN_ACCOUNTS,
    format = tablelib.get_format(),
    country = tablelib.get_country(),
    simplify_mapping = mapping
)
