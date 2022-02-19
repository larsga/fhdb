'''
General, reusable Google Maps library.
'''

import codecs, sys, os, json, string, random
import utils

GOOGLE_MAPS_KEY = os.environ['GOOGLE_MAPS_KEY']

# ===== SHAPES

CIRCLE = 0
SQUARE = 1
TRIANGLE = 2

# ===== CONSTANTS

DEFAULT_STROKEWEIGHT = 2

# ===== MAP

# Next implementation: Leaflet
#   supports custom markers

class AbstractMap:

    def __init__(self, default_scale = 5):
        self._markers = []
        self._symbols = []
        self._legend = False
        self._default_scale = default_scale
        self._show_unused_symbols = False

    def get_color(self):
        return True

    def get_markers(self):
        return self._markers

    def add_marker(self, lat, lng, title, symbol, desc = None, data = None):
        m = Marker(lat, lng, title, symbol, desc, data)
        self._markers.append(m)
        return m

    def get_symbols(self):
        return self._symbols

    def add_symbol(self, color, strokecolor = '#000000',
                   strokeweight = None, title = None, scale = None,
                   shape = CIRCLE, label = None, textcolor = None,
                   id = None):
        '''title: name in legend
        label: text inside actual symbol icon'''
        s = Symbol(color, strokecolor, strokeweight, title = title,
                   scale = scale or self._default_scale, shape = shape,
                   label = label, textcolor = textcolor, id = id)
        self._symbols.append(s)
        return s

    def get_symbols(self):
        return self._symbols

    def is_symbol_used(self, symbol):
        for m in self._markers:
            if m.get_symbol() == symbol:
                return True
        return False

    def show_unused_symbols(self):
        return self._show_unused_symbols

    def set_legend(self, legend, show_unused = False):
        self._legend = legend
        self._show_unused_symbols = show_unused

    def has_legend(self):
        return self._legend

    def has_symbols(self):
        return bool(self._symbols)

class GoogleMap(AbstractMap):

    def __init__(self, center_lat, center_lng, zoom):
        AbstractMap.__init__(self)
        self._id = 'map'
        self._center_lat = center_lat
        self._center_lng = center_lng
        self._zoom = zoom

    def get_id(self):
        return self._id

    def get_center_longitude(self):
        return self._center_lng

    def get_center_latitude(self):
        return self._center_lat

    def get_zoom_level(self):
        return self._zoom

    def render_to(self, filename, width = '100%', height = '100%', bottom = '',
                  format = 'html'):
        format = format or 'html'
        assert format == 'html', 'Incorrect format %s' % format
        filename = utils.add_extension(filename, format)

        render(self, filename, width, height, bottom)

        if len(sys.argv) > 1:
            os.system('open ' + filename)


# ===== SYMBOL

class Symbol:

    def __init__(self, color, strokecolor = None, strokeweight = None,
                 title = None, scale = None, shape = None, label = None,
                 textcolor = None, id = None):
        self._id = id or ''.join([random.choice(string.ascii_letters)
                                  for i in range(10)])
        self._color = color
        self._strokecolor = strokecolor or color
        self._strokeweight = strokeweight or DEFAULT_STROKEWEIGHT
        self._title = title
        self._scale = scale or 5
        self._shape = shape
        self._label = label
        self._textcolor = textcolor

    def get_id(self):
        return self._id

    def get_color(self):
        return self._color

    def get_stroke_color(self):
        return self._strokecolor

    def get_stroke_weight(self):
        return self._strokeweight

    def get_scale(self):
        return self._scale

    def get_title(self):
        return self._title

    def get_shape(self):
        return self._shape

    def get_label(self):
        return self._label

    def get_text_color(self):
        return self._textcolor

    def render_to(self, outf):
        outf.write('''
var %s = {
  fillColor: "%s",
  strokeColor: "%s",
  strokeWeight: %s,
  fillOpacity: 1,
  path: google.maps.SymbolPath.CIRCLE,
  scale: %s
};
        ''' % (self._id, self._color, self._strokecolor, self._strokeweight, self._scale))

# ===== MARKER

class Marker:

    def __init__(self, lat, lng, title, symbol, desc = None, data = None):
        self._lat = lat
        self._lng = lng
        self._title = title
        self._symbol = symbol
        self._desc = desc
        self._data = data

    def get_id(self):
        return u'id%s' % id(self)

    def get_latitude(self):
        return self._lat

    def get_longitude(self):
        return self._lng

    def get_title(self):
        return self._title

    def get_symbol(self):
        return self._symbol

    def get_description(self):
        return self._desc

    def get_data(self):
        return self._data

# ===== RENDERING

def to_jstr(value):
    if value == None:
        return 'null'

    return "'%s'" % value.replace("'", "\\'")

def render(themap, filename, width = '100%', height = '100%', bottom = ''):
    outf = codecs.open(filename, 'w', 'utf-8')
    outf.write(u'''
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<script src="https://maps.googleapis.com/maps/api/js?sensor=false&key=%s" type="text/javascript"></script>
<style>
body {
  font-family: Arial, sans-serif;
}
div.listing {
  display: none;
  width: 500px;
}
div.infowindow {
  display: normal;
  width: 350px;
  font-size: 8pt;
}
#legend {
  background: #fff;
  padding: 10px;
  margin: 10px;
  border: 3px solid #000;
}
</style>

<div id="%s" style="width: %s; height: %s"></div>

<script type="text/javascript">
var mapOptions = {
  center: new google.maps.LatLng(%s, %s),
  zoom: %s,
  streetViewControl: false,
  mapTypeControl: false
};
var map = new google.maps.Map(document.getElementById('%s'), mapOptions);

var markers = [];
var marker_dict = {};

function add_marker(theid, lat, lng, title, symbol, label, textcolor, data) {
  var thelabel = null;
  if (label != null) {
    thelabel = new google.maps.Marker({
      text: label,
      color: textcolor
    });
  }

  var marker = new google.maps.Marker({
      position: new google.maps.LatLng(lat, lng),
      map: map,
      title: title,
      icon: symbol,
      label: thelabel
  });

  marker.popupid = theid;
  marker.data = data;
  markers.push(marker);
  marker_dict[theid] = marker;

  google.maps.event.addListener(marker, 'click', function() {
    // retrieve the element to show in the window
    var element = document.getElementById(marker.popupid);

    // we can't pass this element in because it gets destroyed
    // once the window is closed, so we make a copy
    element = element.cloneNode(true);

    // we want the copy displayed small, so we change the class
    element.className = 'infowindow';

    // switch display from off to on
    element.style.display = "";

    var infowindow = new google.maps.InfoWindow({
      content: element
    });

    infowindow.open(map, marker);
  });

  return marker;
}
    ''' % (GOOGLE_MAPS_KEY,
           themap.get_id(),
           width,
           height,
           themap.get_center_latitude(),
           themap.get_center_longitude(),
           themap.get_zoom_level(),
           themap.get_id()))

    for symbol in themap.get_symbols():
        symbol.render_to(outf)

    for marker in themap.get_markers():
        outf.write(u"add_marker('%s', %s, %s, %s, %s, %s, %s, %s);\n" %
                   (marker.get_id(),
                    marker.get_latitude(),
                    marker.get_longitude(),
                    to_jstr(marker.get_title()),
                    marker.get_symbol().get_id(),
                    to_jstr(marker.get_symbol().get_label()),
                    to_jstr(marker.get_symbol().get_text_color()),
                    json.dumps(marker.get_data())))

    outf.write(u'</script>\n\n\n')

    if themap.has_legend():
        outf.write('<div id="legend">\n')
        for symbol in themap.get_symbols():
            outf.write('''
              <svg height="19" width="16">
                <circle cx="8" cy="13" r="5" stroke="black" stroke-width="1"
                        fill="%s" />
              </svg> %s<br>
            ''' % (symbol.get_color(), symbol.get_title()))
        outf.write('</div>\n')

        outf.write('''
          <script>
            var legend = document.getElementById('legend');
            map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(legend);
          </script>
        ''')

    for marker in themap.get_markers():
        desc = marker.get_description() or ''
        outf.write(u'''
          <div id="%s" class="listing">
            %s<br>%s</div>
        ''' % (marker.get_id(), marker.get_title(), desc))

    outf.write(bottom)
    outf.close()
