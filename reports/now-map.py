'''
Shows where brewing is currently alive.
'''

import maplib
import sparqllib

themap = maplib.Map(61.405343, 9.637301, 6)

alive = themap.add_symbol('green', '#00FF00', '#000000')

query = '''
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>

select ?title ?place ?lat ?lng where {
  ?s dc:title ?title;
    tb:year ?year;
    tb:place-of-origin ?p;
    tb:brewing-ended false.

  ?p rdfs:label ?place;
    geo:lat ?lat;
    geo:long ?lng.

  FILTER ( ?year >= 2000 )
}
'''
for (title, place, lat, lng) in sparqllib.query_for_rows(query):
    themap.add_marker(lat, lng, title, alive)

# ===== RENDER

themap.render_to('now-map.html')