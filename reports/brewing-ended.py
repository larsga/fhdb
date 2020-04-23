
import sparqllib, maplib, config

def get_last_part(uri):
    pos = uri.rfind('/')
    return uri[pos + 1 : ].replace('-', '_')

query = '''
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT DISTINCT ?s ?lat ?lng ?title ?ended
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:brewing-ended ?ended.
}'''

q = '''
prefix neg: <http://www.garshol.priv.no/2014/neg/>
select ?y where { <%s> neg:date ?y }
'''

q2 = '''
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
select ?y where { <%s> tb:year ?y }
'''

q3 = '''
select ?t where { <%s> a ?t }
'''

NEG_RESPONSE = 'http://www.garshol.priv.no/2014/neg/Response'

responses = []
for (s, lat, lng, title, ended) in sparqllib.query_for_rows(query):
    DEBUG = title.find('Bleie') != -1
    year = None
    if ended == u'false':
        year = sparqllib.query_for_value(q % s)

        if not year:
            year = sparqllib.query_for_value(q2 % s)

            if not year:
                if sparqllib.query_for_value(q3 % s) == NEG_RESPONSE:
                    year = 1955

        if type(year) in (type(''), type(u'')):
            year = int(year[: 4])

    if ended == u'false':
        ended = False

    responses.append([s, lat, lng, title, ended, year])

# ===== MAKE MAP

WEIGHT = 1

themap = config.make_map_from_cli_args()

alive = themap.add_symbol('green', '#00FF00', '#000000', WEIGHT)
dead  = themap.add_symbol('black', '#000000', '#000000', WEIGHT)
dunno = themap.add_symbol('gray', '#AAAAAA', '#000000', WEIGHT)

for (s, lat, lng, title, ended, year) in responses:
    number = get_last_part(s)
    themap.add_marker(lat, lng, number + ' - ' + title, alive,
                      'Year: %s, brewing ended: %s' % (year, ended),
                      data = {
                          'ended' : ended,
                          'year'  : year
                      })

bottom = '''
<p>
  <input type=button value="<<" onclick="change_year(-10);">
  <input type=text value="1850" size=4 name=year id=year disabled>
  <input type=button value=">>" onclick="change_year(10);">

<script>
function change_year(inc) {
  var year = parseInt(document.getElementById('year').value);
  if ((year >= 2010 && inc > 0) || (year <= 1850 && inc < 0))
    return;
  year = year + inc;
  document.getElementById('year').value = year;

  for (var i = 0; i < markers.length; i++) {
    var marker = markers[i];

    var icon = null;
    if (!marker.data.ended) {
      if (marker.data.year > year)
        icon = green;
      else
        icon = gray;
    } else {
      if (marker.data.ended > year)
        icon = green;
      else
        icon = black;
    }

    marker.setIcon(icon);
  }
}
</script>
'''

themap.render_to('brewing-ended.html',
                 height = '95%',
                 bottom = bottom)
