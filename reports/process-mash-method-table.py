# encoding=utf-8

import argparse
import codecs
import sparqllib
import tablelib
import proclib

parser = argparse.ArgumentParser()
parser.add_argument('--lang', default = 'en')
args = parser.parse_args()

LANG = args.lang
predicates = {
    'infusion' : proclib.Process.is_single_infusion,
    'step' : proclib.Process.is_multistep_infusion,
    'decoction' : proclib.Process.is_decoction,
    'circulation' : proclib.Process.is_circulation,
    'kettle' : proclib.Process.is_kettle_mash,
    'mashboil' : proclib.Process.is_mash_boiled,
    'stones' : proclib.Process.is_stone_mash,
}
col_labels = {
    'en' : {
        'infusion' : 'Infusion',
        'step' : 'Step mash',
        'decoction' : 'Decoction',
        'circulation' : 'Circulation',
        'kettle' : 'In kettle',
        'mashboil' : 'Boiled mash',
        'stones' : 'Stones',
    },
    'no' : {
        'infusion' : 'Infusjon',
        'step' : 'Stegmesk',
        'decoction' : 'Dekoksjon',
        'circulation' : 'Sirkulering',
        'kettle' : 'I kjele',
        'mashboil' : 'Kokt mesk',
        'stones' : 'Steiner',
    },
}[LANG]

processes = proclib.load_process_dict()
table = tablelib.CountryTable(1, lang = LANG)
regiontype = '<http://www.garshol.priv.no/2021/landsdel/Landsdel>'
#regiontype = 'dbp:Country'

labels = {uri : label for (uri, label) in sparqllib.query_for_rows('''
  select ?uri ?label where {
    ?uri a %s; rdfs:label ?label
  }
''' % regiontype)}

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>

SELECT ?s ?lat ?lng ?proc ?title ?ld
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:process ?proc.

  ?s tb:part-of ?ld.
  ?ld a %s.
}''' % regiontype
for (s, lat, lng, proc, title, where) in sparqllib.query_for_rows(query):
    proc = processes[proc]
    if not proc.is_mashing_fully_defined():
        continue

    for (name, predicate) in predicates.items():
        if predicate(proc):
            table.add_account(name, where, s)

filename = 'process-mash-method-table.html'
writer = tablelib.HtmlWriter(codecs.open(filename, 'w', 'utf-8'))
tablelib.write_table(
    writer, table, lambda col: col_labels[str(col)],
    lang = LANG,
    get_row_label = lambda uri: labels[uri]
)
