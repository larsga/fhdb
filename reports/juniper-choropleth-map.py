
import mapniklib, sparqllib, utils, config

JUNIPER = 'http://www.garshol.priv.no/2014/neg/juniper'

district_query = '''
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
SELECT ?districtn
WHERE {
  ?district a <http://www.garshol.priv.no/2021/district/District>;
    rdfs:label ?districtn.
}
'''

query = '''
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
SELECT ?s ?inf ?h ?districtn
WHERE {
  ?s
    dc:title ?title;
    tb:herbs ?h.

  ?district a <http://www.garshol.priv.no/2021/district/District>;
    tb:contains ?s;
    rdfs:label ?districtn.

  OPTIONAL {
    ?s tb:juniper-infusion ?inf.
  }
}'''

accounts = {}
for (s, inf, herb, districtn) in sparqllib.query_for_rows(query):
    inf = (inf == 'true')
    already_juniper = accounts.get(s, (None, False, None))[1]
    accounts[s] = (inf, already_juniper or herb == JUNIPER, districtn)

accounts = [
    (districtn, (0.75 + (0.25 if inf else 0)) if juniper else 0)
    for (inf, juniper, districtn) in accounts.values()
]

district_index = utils.index(accounts)

from pprint import pprint
# pprint(district_index)

district_to_value = {name : utils.average(points)
                     for (name, points) in district_index.items()}
for (district_name) in sparqllib.query_for_list(district_query):
    if district_name not in district_to_value:
        district_to_value[district_name] = None # means: no data

pprint(district_to_value)

themap = config.make_map_from_cli_args(map_type = 'choropleth')
themap.render_to('juniper-choropleth-map', district_to_value)
