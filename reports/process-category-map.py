# encoding=utf-8

import config
import sparqllib
import proclib

themap = config.make_map_from_cli_args()

symbols = {
    None : themap.add_symbol('#000000', '#000000', strokeweight = 1,
                             title = 'Unclassified'),
    'Stone' : themap.add_symbol('#00FF00', '#000000',
                                title = 'Stone', strokeweight = 1),
    'Ferment mash' : themap.add_symbol('#42DFFF', '#000000',
                                       title = 'Ferment mash', strokeweight = 1),
    'Oven' : themap.add_symbol('#FFFF00', '#000000',
                               title = 'Oven', strokeweight = 1),
    'Complex mash' : themap.add_symbol('#4444FF', '#000000',
                               title = 'Complex mash', strokeweight = 1),
    'Raw ale' : themap.add_symbol('#FF8800', '#000000',
                                  title = 'Raw ale', strokeweight = 1),
    'Boiled' : themap.add_symbol('#FFFFFF', '#000000',
                                  title = 'Boiled', strokeweight = 1),
}

process_categories = proclib.classify_processes()

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

    cat = process_categories.get(proc)
    if cat == None:
        #print('UNMAPPED', repr(proc))
        continue

    #print(proc, cat)
    themap.add_marker(lat, lng, title, symbols[cat], procname)

themap.set_legend(True)
themap.render_to(config.get_file() or 'process-category-map')
