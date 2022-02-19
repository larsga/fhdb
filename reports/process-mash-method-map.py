# encoding=utf-8
'''
Map of where a specific mashing method is used or not used.
'''

import config
import sparqllib
import proclib

predicates = {
    'step' : proclib.Process.is_multistep_infusion,
    'decoction' : proclib.Process.is_decoction,
    'circulation' : proclib.Process.is_circulation,
    'kettle' : proclib.Process.is_kettle_mash,
    'mashboil' : proclib.Process.is_mash_boiled,
}
config.parser.add_argument('--method', required = True,
                           choices = predicates.keys())

themap = config.make_map_from_cli_args()

symbols = {
    'False' : themap.add_symbol('#000000', '#000000', strokeweight = 1,
                                title = 'Not used'),
    'True' : themap.add_symbol('#FFFF00', '#000000',
                                title = 'Used', strokeweight = 1),
}
predicate = predicates[config._get_args().method]

processes = proclib.load_process_dict()

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT ?s ?lat ?lng ?proc ?title ?procname
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:process ?proc.

  ?proc rdfs:label ?procname.
}'''
for (s, lat, lng, proc, title, procname) in sparqllib.query_for_rows(query):
    proc = processes[proc]
    if not proc.is_mashing_fully_defined():
        continue

    symbol = symbols[str(predicate(proc))]
    themap.add_marker(lat, lng, title, symbol, '%s: %s' % (proc.get_no(), procname))

themap.set_legend(True)
themap.render_to('process-mash-method-map')
