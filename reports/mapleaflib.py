# encoding=utf-8
'''
Map implementation using Leaflet.js
'''

import sys, os
import maplib

class LeafletMap(maplib.AbstractMap):

    def __init__(self, center_lat, center_lng, zoom):
        maplib.AbstractMap.__init__(self)
        self._id = 'map'
        self._center_lat = center_lat
        self._center_lng = center_lng
        self._zoom = zoom

    # identical to google maps method
    def get_id(self):
        return self._id

    # identical to google maps method
    def get_center_longitude(self):
        return self._center_lng

    # identical to google maps method
    def get_center_latitude(self):
        return self._center_lat

    # identical to google maps method
    def get_zoom_level(self):
        return self._zoom

    # identical to google maps method
    def render_to(self, filename, width = '100%', height = '100%', bottom = '',
                  format = 'html'):
        format = format or 'html'
        assert format == 'html', 'Incorrect format %s' % format
        if not filename.endswith('.html'):
            filename += '.html'

        render(self, filename, width, height, bottom)

        if len(sys.argv) > 1:
            os.system('open ' + filename)

# ===========================================================================
# RENDERING

def render(themap, filename, width, height, bottom):
    f = open(filename, 'w')
    f.write('''
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"
   integrity="sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A=="
   crossorigin=""/>
<script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"
   integrity="sha512-XQoYMqMTK8LvdxXYG3nZ448hOEQiglfqkJs1NOQV44cWnUrBc8PkAOcXy20w0vlaXaVUearIOBhiXZ5V3ynxwA=="
   crossorigin=""></script>
<div id="%s"></div>
<style>
  #map {
    width: %s;
    height: %s;
  }

.legend {
    line-height: 18px;
    color: #555;
}
.legend i {
    width: 18px;
    height: 18px;
    float: left;
    margin-right: 8px;
    opacity: 0.7;
}
.info {
    padding: 6px 8px;
    font: 14px/16px Arial, Helvetica, sans-serif;
    background: white;
    background: rgba(255,255,255,0.8);
    box-shadow: 0 0 15px rgba(0,0,0,0.2);
    border-radius: 5px;
}
</style>

<script>
  var icons = {
''' % (themap.get_id(), width, height))

    for (ix, symbol) in enumerate(themap.get_symbols()):
        fname = '/tmp/%s.svg' % symbol.get_id()
        symbol.generate_svg(fname)
        f.write(' "%s" : `%s` ' % (symbol.get_id(), open(fname).read()))

        if ix + 1 < len(themap.get_symbols()):
            f.write(',\n')

    f.write('''
  }
  var mymap = L.map('map').setView([%s, %s], %s);

  L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoibGFyc2dhIiwiYSI6ImNrdmtucGR0aDM3cGUycHBndzBxYXdoazQifQ.KGr_qFA8yMDYmACvfrU28Q'
}).addTo(mymap);
''' % (themap.get_center_latitude(), themap.get_center_longitude(),
       themap.get_zoom_level()))

    for marker in themap.get_markers():
        f.write('''
        L.marker([%s, %s], {
          'title' : '%s',
          'icon' : L.divIcon({"html" : icons["%s"], "className" : "",
                              "iconSize" : [12, 12]})
        }).addTo(mymap);\n''' % (
            marker.get_latitude(), marker.get_longitude(), marker.get_title(),
            marker.get_symbol().get_id()
        ))

    labels = ['<i class=circle style="background: %s"></i> %s' %
              (s.get_color(), s.get_title()) for s in themap.get_symbols()]

    f.write('''
      var legend = L.control({position: 'topright'});
      legend.onAdd = function (map) {
        var div = L.DomUtil.create('div', 'info legend');
        div.innerHTML = `%s`;
        return div;
      };
      legend.addTo(mymap);
    ''' % '<br><br>'.join(labels))

    f.write('</script>\n')
    f.close()
