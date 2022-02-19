# encoding=utf-8
'''
A map of the main method by which the mash was heated. Not a heatmap, but
a map of heating methods.
'''

import config
import sparqllib
import proclib

def get_no(url):
    return url[url.rfind('/') + 1 : ]

themap = config.make_map_from_cli_args()

symbols = {
    None : themap.add_symbol('black', '#000000', '#000000', strokeweight = 1,
                             title = 'Unclassified'),
    'Stone' : themap.add_symbol('green', '#00FF00', '#000000',
                                title = 'Stone', strokeweight = 1),
    'Kettle' : themap.add_symbol('kettle', '#42DFFF', '#000000',
                                 title = 'Kettle', strokeweight = 1),
    'Oven' : themap.add_symbol('yellow', '#FFFF00', '#000000',
                               title = 'Oven', strokeweight = 1),
    'Mixed' : themap.add_symbol('mixed', '#4444FF', '#000000',
                               title = 'Mixed', strokeweight = 1),
    'External' : themap.add_symbol('external', '#FF8800', '#000000',
                                  title = 'External', strokeweight = 1),
    'Infusion' : themap.add_symbol('infusion', '#FFFFFF', '#000000',
                                  title = 'Infusion', strokeweight = 1),
}

process_categories = proclib.classify_main_heating()

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

    if config.get_debug():
        print(proc, cat)
    themap.add_marker(lat, lng, title, symbols[cat], get_no(proc) + ': ' + procname)

themap.set_legend(True)
themap.render_to('process-main-heat-map')
