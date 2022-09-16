# encoding=utf-8

import config
import sparqllib
import proclib

themap = config.make_map_from_cli_args()
labels = {
    'en' : {
        None      : 'Unclassified',
        'stone'   : 'Stone',
        'boiled'  : 'Boiled',
        'raw'     : 'Raw ale',
        'complex' : 'Complex mash',
        'fermash' : 'Ferment mash',
        'oven'    : 'Oven',
    },
    'no' : {
        None      : 'Uklassifisert',
        'stone'   : 'Steinøl',
        'boiled'  : 'Kokt vørter',
        'raw'     : 'Råøl',
        'complex' : 'Kompleks mesk',
        'fermash' : 'Gjæret mesk',
        'oven'    : 'Ovn',
    }
}[config.get_language()]

symbols = {
    None : themap.add_symbol('#000000', '#000000', strokeweight = 1,
                             title = labels[None]),
    'Stone' : themap.add_symbol('#00FF00', '#000000',
                                title = labels['stone'], strokeweight = 1),
    'Ferment mash' : themap.add_symbol('#42DFFF', '#000000', strokeweight = 1,
                                       title = labels['fermash']),
    'Oven' : themap.add_symbol('#FFFF00', '#000000', strokeweight = 1,
                               title = labels['oven']),
    'Complex mash' : themap.add_symbol('#4444FF', '#000000', strokeweight = 1,
                                       title = labels['complex']),
    'Raw ale' : themap.add_symbol('#FF8800', '#000000', strokeweight = 1,
                                  title = labels['raw']),
    'Boiled' : themap.add_symbol('#FFFFFF', '#000000', strokeweight = 1,
                                  title = labels['boiled']),
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
        print('UNMAPPED', repr(proc))
        continue

    #print(proc, cat)
    themap.add_marker(lat, lng, title, symbols[cat], procname)

themap.set_legend(True)
themap.render_to(config.get_file() or 'process-category-map')
