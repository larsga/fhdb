'''
Implementation of the Map class which generates PNG maps using Mapnik.
'''

import json, sys, os, random, string
import mapnik
import maplib

SHAPEDIR = os.environ.get('SHAPEDIR') # shapefiles must be located here

# download from http://www.naturalearthdata.com/downloads/
#  - ne_10m_admin_0_countries
#  - ne_10m_lakes
#  - ne_10m_glaciated_areas
#  - ne_10m_rivers_lake_centerlines

if not SHAPEDIR.endswith('/'):
    SHAPEDIR += '/'

ELEVATION_DEFAULT = False

#district_file = None
#district_file = '/Users/larsga/prog/python/etno-distrikt/landsdeler.json'
#district_file = '/Users/larsga/prog/python/etno-distrikt/regions.json'
#district_file = '/Users/larsga/prog/python/etno-distrikt/regions-clipped.json'

# ===== BASE MAP
# A base map is the actual geography rendering without symbols or legends.
# These can be of different kinds.

class BaseMap:

    def get_transform(self):
        'Post-rendering transform function.'
        return None

    def make_map(self):
        'Produces a configured mapnik map for the base.'
        raise NotImplementedError()

# ===== FULL MAP
# A full map is the base + symbols/legend

class MapnikMap(maplib.AbstractMap):

    def __init__(self, base_map, color = True, transform = None):
        maplib.AbstractMap.__init__(self, default_scale = 8)
        self._base_map = base_map
        self._color = color
        self._transform = transform
        self._legend_location = ('top', 'left')

    def get_base_map(self):
        return self._base_map

    def get_color(self):
        return self._color

    def add_line_string(self, geojson, color, width):
        if isinstance(self._base_map, ColoredRegionMap):
            self._base_map.add_line_string(geojson, color, width)
        else:
            render_line_string(self._base_map._mapnik_map)

    def add_shaded_region(self, shape, color = 'rgb(0%, 0%, 0%)', opacity = 0.15):
        m = self._base_map._mapnik_map
        _add_shaded_region(m, shape = shape, color = color, opacity = opacity)

    def add_rectangle(self, east, west, north, south, color, width = 1):
        m = self._base_map._mapnik_map

        s = mapnik.Style()
        r = mapnik.Rule()

        line_symbolizer = mapnik.LineSymbolizer()
        line_symbolizer.stroke = mapnik.Color(color)
        line_symbolizer.stroke_width = width
        r.symbols.append(line_symbolizer)
        s.rules.append(r)

        m.append_style('CustomRectangle',s)

        fname = '/tmp/geojson-%s.json' % random_id()
        with open(fname, 'w') as f:
            json.dump({
                "type": "FeatureCollection",
                "name": "rectangle",
                "features": [{
                    'type' : 'Feature',
                    'geometry' : {
                        'type' : 'Polygon',
                        'coordinates' : [[(west, north), (east, north),
                                          (east, south), (west, south),
                                          (west, north)]]
                    }
                }]
            }, f)

        ds = mapnik.GeoJSON(file = fname)
        layer = mapnik.Layer('rectangle')

        layer.datasource = ds
        layer.srs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
        layer.styles.append('CustomRectangle')
        m.layers.append(layer)

    def set_legend_location(self, vertical, horizontal):
        self._legend_location = (vertical, horizontal)

    def render_to(self, filename, width = None, height = None, bottom = None,
                  format = 'png', preview = True):
        format = format or 'png'
        filename = make_ending_for(filename, format)
        legend_box = _render(self, filename, format, self._legend_location)

        transform = self._base_map.get_transform() or self._transform
        if transform:
            transform(filename, legend_box)

        if preview and len(sys.argv) > 1:
            os.system('open ' + filename)

def make_ending_for(filename, format):
    ending = '.' + format
    if not filename.endswith(ending):
        filename += ending
    return filename

# ===== SETUP

class Colors:
    def __init__(self, **entries):
        self.__dict__.update(entries)

default_colors = Colors(
    water_color = '#88CCFF',
    land_color = '#409050'
)
black_and_white = Colors(
    water_color = '#F6F6F6',
    land_color = '#BBBBBB',
)

# ===== SIMPLE BASE MAP

class SimpleBaseMap(BaseMap):

    def __init__(self, mapnik_map):
        self._mapnik_map = mapnik_map

    def make_map(self):
        return self._mapnik_map

def make_simple_map(shapefile = None, west = -5, south = 55, east = 35, north = 67, width = 2000, height = 1200, elevation = ELEVATION_DEFAULT, color = True, speciesfile = None, district_file = None, district_line_width = 0.5):
    if color:
        colors = default_colors
    else:
        colors = black_and_white

    m = mapnik.Map(width, height)
    m.srs = '+proj=merc +ellps=WGS84 +datum=WGS84 +no_defs'
    m.background = mapnik.Color(colors.water_color)

    shapefile = shapefile or (SHAPEDIR + 'ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp')

    _add_green_land(m, shapefile, colors)
    if elevation:
        _add_elevation(m)
    _add_borders(m, shapefile, colors)

    _add_lakes(m, colors)
    _add_rivers(m, colors)
    _add_glaciers(m)

    if speciesfile:
        _add_shaded_region(m, jsonfile = speciesfile, color = 'black', opacity = 0.25)
    if district_file:
        _add_districts(m, district_file, district_line_width)

    zoom_to_box(m, west, south, east, north)
    return SimpleBaseMap(m)

def project(srs, west, south, east, north):
    source = mapnik.Projection('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    target = mapnik.Projection(srs)
    trans = mapnik.ProjTransform(source, target)
    thebox = mapnik.Box2d(west, south, east, north)
    return trans.forward(thebox)

def zoom_to_box(m, west, south, east, north):
    # the box is defined in degrees when passed in to us, but now that
    # the projection is Mercator, the bounding box must be specified
    # in metres (no, I don't know why). we solve this by explicitly
    # converting degrees to metres
    m.zoom_to_box(project(m.srs, west, south, east, north))

def _add_green_land(m, shapefile, colors):
    s = mapnik.Style() # style object to hold rules

    r = mapnik.Rule() # rule object to hold symbolizers
    # to fill a polygon we create a PolygonSymbolizer
    polygon_symbolizer = mapnik.PolygonSymbolizer()
    polygon_symbolizer.fill = mapnik.Color(colors.land_color)
    r.symbols.append(polygon_symbolizer) # add the symbolizer to the rule object
    s.rules.append(r) # now add the rule to the style

    m.append_style('My Style',s)

    ds = mapnik.Shapefile(file = shapefile)
    layer = mapnik.Layer('world')

    layer.datasource = ds
    layer.srs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    layer.styles.append('My Style')

    m.layers.append(layer)

def _add_borders(m, shapefile, colors):
    s = mapnik.Style() # style object to hold rules

    r = mapnik.Rule() # rule object to hold symbolizers

    # to add outlines to a polygon we create a LineSymbolizer
    line_symbolizer = mapnik.LineSymbolizer()
    line_symbolizer.stroke = mapnik.Color('rgb(10%,10%,10%)')
    line_symbolizer.stroke_width = 0.5
    r.symbols.append(line_symbolizer) # add the symbolizer to the rule object
    s.rules.append(r) # now add the rule to the style

    m.append_style('My Style2',s)

    ds = mapnik.Shapefile(file = shapefile)
    layer = mapnik.Layer('world2')

    layer.datasource = ds
    layer.srs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    layer.styles.append('My Style2')

    m.layers.append(layer)

def random_id():
    return ''.join([random.choice(string.ascii_letters) for ix in range(10)])

def _add_shaded_region(m, shape = None, opacity = 0.25, color = 'rgb(0%,0%,0%)',
                       jsonfile = None):
    '''shape = geojson shape object for region
    jsonfile = geojson file containing region'''

    s = mapnik.Style() # style object to hold rules
    r = mapnik.Rule() # rule object to hold symbolizers
    # to fill a polygon we create a PolygonSymbolizer
    polygon_symbolizer = mapnik.PolygonSymbolizer()
    polygon_symbolizer.fill = mapnik.Color(color)
    polygon_symbolizer.fill_opacity = opacity
    r.symbols.append(polygon_symbolizer) # add the symbolizer to the rule object

    # to add outlines to a polygon we create a LineSymbolizer
    line_symbolizer = mapnik.LineSymbolizer()
    line_symbolizer.stroke = mapnik.Color(color)
    line_symbolizer.stroke_width = 1
    r.symbols.append(line_symbolizer) # add the symbolizer to the rule object
    s.rules.append(r) # now add the rule to the style

    the_id = random_id()
    m.append_style(the_id, s)

    if shape:
        with open('/tmp/region.json', 'w') as f:
            json.dump({'type': 'FeatureCollection', 'features' : [shape]}, f)
        jsonfile = '/tmp/region.json'
    elif not jsonfile:
        assert False, 'Must specify either shape or jsonfile'

    if jsonfile.endswith('.json'):
        ds = mapnik.GeoJSON(file = jsonfile)
    elif jsonfile.endswith('.shp'):
        ds = mapnik.Shapefile(file = jsonfile)
    else:
        assert False

    layer = mapnik.Layer(random_id())

    layer.datasource = ds
    layer.srs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    layer.styles.append(the_id)

    m.layers.append(layer)

def _add_districts(m, district_file, district_line_width):
    s = mapnik.Style()
    r = mapnik.Rule()

    # polygon_symbolizer = mapnik.PolygonSymbolizer()
    # polygon_symbolizer.fill = mapnik.Color('rgb(0,0,0)')
    # polygon_symbolizer.fill_opacity = 0.25
    # r.symbols.append(polygon_symbolizer)

    line_symbolizer = mapnik.LineSymbolizer()
    line_symbolizer.stroke = mapnik.Color('rgb(0%,0%,0%)')
    line_symbolizer.stroke_width = district_line_width
    r.symbols.append(line_symbolizer)
    s.rules.append(r)

    m.append_style('districts',s)

    ds = mapnik.GeoJSON(file = district_file)
    layer = mapnik.Layer('districts')

    layer.datasource = ds
    layer.srs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    layer.styles.append('districts')

    m.layers.append(layer)

def _make_transform(source, target):
    source = mapnik.Projection(source)
    target = mapnik.Projection(target)
    trans = mapnik.ProjTransform(source, target)
    return trans

def _add_lakes(m, colors):
    s = mapnik.Style()
    r = mapnik.Rule()
    polygon_symbolizer = mapnik.PolygonSymbolizer()
    polygon_symbolizer.fill = mapnik.Color(colors.water_color)
    r.symbols.append(polygon_symbolizer)
    s.rules.append(r)

    m.append_style('LakeStyle', s)

    ds = mapnik.Shapefile(file = SHAPEDIR + 'ne_10m_lakes/ne_10m_lakes.shp')
    layer = mapnik.Layer('lakes')
    layer.datasource = ds
    # https://help.openstreetmap.org/questions/13250/what-is-the-correct-projection-i-should-use-with-mapnik
    layer.srs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    layer.styles.append('LakeStyle')
    m.layers.append(layer)

def _add_glaciers(m):
    s = mapnik.Style()
    r = mapnik.Rule()
    polygon_symbolizer = mapnik.PolygonSymbolizer()
    polygon_symbolizer.fill = mapnik.Color('#eeeeee')
    r.symbols.append(polygon_symbolizer)
    s.rules.append(r)

    line_symbolizer = mapnik.LineSymbolizer()
    line_symbolizer.stroke = mapnik.Color('#000077')
    line_symbolizer.stroke_width = 1
    r.symbols.append(line_symbolizer)
    s.rules.append(r)

    m.append_style('GlacierStyle', s)

    ds = mapnik.Shapefile(file = SHAPEDIR + 'ne_10m_glaciated_areas/ne_10m_glaciated_areas.shp')
    layer = mapnik.Layer('glaciers')
    layer.datasource = ds
    layer.srs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    layer.styles.append('GlacierStyle')
    m.layers.append(layer)

def _add_elevation(m):
    s = mapnik.Style()
    r = mapnik.Rule()
    # rs = mapnik.RasterSymbolizer()
    # rs.opacity = 1.0
    # rs.scaling = 'bilinear'
    # rs.comp_op = 'multiply'

    rs = mapnik.RasterSymbolizer()

    # COLORIZER_DISCRETE is a binned/classified renderer.
    # Other options are COLORIZER_LINEAR (stretched) and
    # COLORIZER_EXACT (unique)
    rs.colorizer = mapnik.RasterColorizer(
        mapnik.COLORIZER_LINEAR, mapnik.Color(0, 0, 0, 0)
    )

    rs.colorizer.add_stop(10, mapnik.Color(64, 144, 80))
    # rs.colorizer.add_stop(250, mapnik.Color(58, 130, 72))
    # rs.colorizer.add_stop(500, mapnik.Color(37, 117, 69)) # green
    # rs.colorizer.add_stop(1000, mapnik.Color(27, 75, 46)) # green
    # rs.colorizer.add_stop(2000, mapnik.Color(0, 0, 0))

    #rs.colorizer.add_stop(10, mapnik.Color(89, 165, 98))

    rs.colorizer.add_stop(250, mapnik.Color(58, 130, 72))
    rs.colorizer.add_stop(500, mapnik.Color(37, 117, 69)) # green
    rs.colorizer.add_stop(750, mapnik.Color(27, 75, 46)) # green
    rs.colorizer.add_stop(1000, mapnik.Color(115, 29, 14))  # brown
    rs.colorizer.add_stop(2000, mapnik.Color(0, 0, 0))

    # rs.colorizer.add_stop(250, mapnik.Color(58, 130, 72))
    # rs.colorizer.add_stop(500, mapnik.Color(37, 117, 69)) # green
    # rs.colorizer.add_stop(1000, mapnik.Color(27, 75, 46)) # green
    # rs.colorizer.add_stop(2000, mapnik.Color(0, 0, 0))

    r.symbols.append(rs)
    s.rules.append(r)

    m.append_style('HillShade', s)

    # old ETOPO5 data from 1988 with poor resolution
    # https://www.eea.europa.eu/data-and-maps/data/world-digital-elevation-model-etopo5
    # ds = mapnik.Gdal(
    #     base = '/Users/larsga/Desktop/DEM_geotiff',
    #     file = 'alwdgg.tif',
    #     band = 1,
    # )
    # srs = '+proj=longlat +ellps=clrk66 +no_defs'

    # new, huge EU-EDM v1.0
    # https://land.copernicus.eu/imagery-in-situ/eu-dem/eu-dem-v1-0-and-derived-products
    # The x,y-coordinates in the tiles are based on the EPSG:3035
    # (ETRS89-LAEA) projection. ->
    # ds = mapnik.Gdal(
    #     base = '/Users/larsga/Desktop/EUDEM1',
    #     file = 'EUD_CP-DEMS_4500045000-AA.tif',
    #     band = 1,
    # )
    # srs = '+proj=laea +lat_0=52 +lon_0=10 +x_0=4321000 +y_0=3210000 +ellps=GRS80 +units=m +no_defs'

    # ETOPO1
    # https://www.ngdc.noaa.gov/mgg/global/
    ds = mapnik.Gdal(
        base = SHAPEDIR + '/ETOPO1',
        file = 'ETOPO1_Ice_c_geotiff.tif',
        band = 1,
    )
    srs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'

    # ds = mapnik.Gdal(
    #     base = SHAPEDIR + '/DTM50_UTM33_20200904',
    #     file = '7405_50m_33.tif', #'norge.tif',
    #     band = 1,
    # )
    # srs = '+proj=utm +zone=33 +ellps=WGS84 +datum=WGS84 +units=m +no_defs'

    # ds = mapnik.Gdal(
    #     base = '/Users/larsga/Desktop/Nedlastingspakke/',
    #     file = '6400_1_10m_z33.tif',
    #     band = 1,
    # )
    # srs = '+proj=utm +zone=33 +ellps=WGS84 +datum=WGS84 +units=m +no_defs'

    layer = mapnik.Layer('Elevation')
    layer.datasource = ds
    layer.srs = srs

    layer.styles.append('HillShade')
    m.layers.append(layer)

def _add_rivers(m, colors):
    s = mapnik.Style()
    r = mapnik.Rule()
    r.filter = mapnik.Filter("[name] = 'Volga' or [name] = 'Dnipro' or [name] = 'Don' or [name] = 'Kama'")
    line_symbolizer = mapnik.LineSymbolizer()
    line_symbolizer.stroke = mapnik.Color(colors.water_color)
    line_symbolizer.stroke_width = 0.4
    r.symbols.append(line_symbolizer)
    s.rules.append(r)
    m.append_style('RiverStyle', s)

    ds = mapnik.Shapefile(file = SHAPEDIR + 'ne_10m_rivers_lake_centerlines/ne_10m_rivers_lake_centerlines.shp')
    layer = mapnik.Layer('rivers')
    layer.datasource = ds
    layer.srs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    layer.styles.append('RiverStyle')
    m.layers.append(layer)

# ===== RENDERING

def _generate_svg(filename, symbol):
    with open(filename, 'w') as f:
        size = symbol.get_scale() * 2
        mid = symbol.get_scale()

        if symbol.get_shape() == maplib.CIRCLE:
            f.write('''
                <svg viewBox="0 0 %s %s" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="%s" cy="%s" r="%s" stroke="%s" fill="%s"
                          stroke-width="%s"/>
                </svg>
            ''' % (
                size,
                size,
                mid,
                mid,
                mid,
                symbol.get_stroke_color(),
                symbol.get_color(),
                symbol.get_stroke_weight()
            ))

        elif symbol.get_shape() == maplib.SQUARE:
            f.write('''
                <svg viewBox="0 0 %s %s" xmlns="http://www.w3.org/2000/svg">
                  <rect width="%s" height="%s" stroke="%s" fill="%s"/>
                </svg>
            ''' % (
                size,
                size,
                size,
                size,
                symbol.get_stroke_color(),
                symbol.get_color()
            ))

        elif symbol.get_shape() == maplib.TRIANGLE:
            topx = size / 2.0
            topy = 0

            botleftx = 0
            botlefty = size

            botrightx = size
            botrighty = size

            f.write('''
                <svg viewBox="0 0 %s %s" xmlns="http://www.w3.org/2000/svg">
                  <polygon points="%s,%s %s,%s %s,%s"
                           stroke="%s" fill="%s" />
                </svg>
            ''' % (
                size,
                size,
                topx,
                topy,
                botleftx,
                botlefty,
                botrightx,
                botrighty,
                symbol.get_stroke_color(),
                symbol.get_color()
            ))

        else:
            assert False, 'Unknown shape: %s' % symbol.get_shape()

def _render(themap, filename, format, legend_location):
    m = themap.get_base_map().make_map()
    ctx = mapnik.Context()

    symbol_layers = {}
    for symbol in themap.get_symbols():
        assert not(symbol.get_label())

        svgfile = '/tmp/%s.svg' % symbol.get_id()
        _generate_svg(svgfile, symbol)

        ps = mapnik.PointSymbolizer()
        ps.file = svgfile
        ps.allow_overlap = True
        ps.ignore_placement = True

        r = mapnik.Rule()
        r.symbols.append(ps)

        s = mapnik.Style()
        s.rules.append(r)

        m.append_style('symbol_' + symbol.get_id(), s)

    ix = 0
    for marker in themap.get_markers():
        f = mapnik.Feature.from_geojson(json.dumps({
          "type": "Feature",
          "geometry": {
            "type": "Point",
            "coordinates": [float(marker.get_longitude()), float(marker.get_latitude())]
          }
        }), ctx)

        ds = mapnik.MemoryDatasource()
        symbol_layers[symbol.get_id()] = ds

        l = mapnik.Layer('layer_%s' % ix)
        ix += 1
        l.clear_label_cache = True
        l.datasource = ds
        l.styles.append('symbol_' + marker.get_symbol().get_id())

        m.layers.append(l)

        ds.add_feature(f)

    mapnik.render_to_file(m, filename, format)

    box = None
    if themap.has_legend() and themap.has_symbols() and format == 'png':
        used_symbols = [s for s in themap.get_symbols()
                        if themap.is_symbol_used(s) or themap.show_unused_symbols()]
        box = _add_legend(filename, used_symbols, legend_location)
    return box

def _add_legend(filename, used_symbols, legend_location):
    from PIL import Image, ImageDraw, ImageFont

    im = Image.open(filename)

    r = 12
    font = ImageFont.truetype('Arial.ttf', r * 2)

    widest = 0
    for symbol in used_symbols:
        width = font.getsize(symbol.get_title())[0]
        widest = max(widest, width)

    offset = 10
    boxwidth = r * 2 + offset * 3 + widest
    displace = (r * 2) + 12
    boxheight = displace * len(used_symbols) + offset

    (vertpos, horpos) = legend_location
    assert vertpos == 'top'
    assert horpos in ('left', 'right')
    y1 = offset
    y2 = offset + boxheight
    if horpos == 'left':
        x1 = offset
        x2 = offset + boxwidth
    else:
        (width, height) = im.size
        x1 = width - (offset + boxwidth)
        x2 = width - offset

    box = [(x1, y1), (x2, y2)]

    draw = ImageDraw.Draw(im)
    draw.rectangle(
        box,
        outline = (0, 0, 0),
        fill = (255, 255, 255),
        width = 2,
    )

    for ix in range(len(used_symbols)):
        displacement = displace * ix

        symbol = used_symbols[ix]
        if symbol.get_shape() == maplib.CIRCLE:
            draw.ellipse(
                [
                    (x1 + offset, y1 + offset + displacement),
                    (x1 + offset + (r * 2), y1 + offset + (r * 2) + displacement)
                ],
                outline = (0, 0, 0),
                fill = _parse_color(symbol.get_color())
            )

        elif symbol.get_shape() == maplib.TRIANGLE:
            draw.polygon(
                [
                    (x1 + offset + r, y1 + offset + displacement),
                    (x1 + offset, y1 + offset + r*2 + displacement),
                    (x1 + offset + r*2, y1 + offset + r*2 + displacement)
                ],
                outline = (0, 0, 0),
                fill = _parse_color(symbol.get_color())
            )

        else:
            assert False, 'Unsupported shape: %s' % symbol.get_shape()

        draw.text(
            (x1 + 20 + (r * 2), y1 + 8 + displacement),
            text = symbol.get_title(),
            fill = (0, 0, 0),
            font = font,
        )

    #im.show()
    im.save(filename, 'PNG')
    return box

def render_line_string(m, geojson, color, width):
    s = mapnik.Style()
    r = mapnik.Rule()

    line_symbolizer = mapnik.LineSymbolizer()
    line_symbolizer.stroke = mapnik.Color(color)
    line_symbolizer.stroke_width = width
    r.symbols.append(line_symbolizer)
    s.rules.append(r)

    m.append_style('CustomLine',s)

    with open('/tmp/geojson.json', 'w') as f:
        f.write(geojson)
    ds = mapnik.GeoJSON(file = '/tmp/geojson.json')
    layer = mapnik.Layer('linestring')

    layer.datasource = ds
    layer.srs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    layer.styles.append('CustomLine')
    m.layers.append(layer)

def _parse_color(color):
    return (_unhex(color[1 : 3]), _unhex(color[3 : 5]), _unhex(color[5 : 7]))

def _unhex(h):
    return _unhexdigit(h[0]) * 16 + _unhexdigit(h[1])

def _unhexdigit(digit):
    if digit >= '0' and digit <= '9':
        return int(digit)
    else:
        return ord(digit.lower()) - 87

# ===== FREE-FORM COLOUR-FILL MAP

class ColoredRegionMap(BaseMap):

    def __init__(self, view, water_color = None):
        self._view = view
        self._legend = False
        self._district_file = '/Users/larsga/prog/python/etno-distrikt/regions-clipped.json'
        self._label_formatter = lambda x,y: '%s-%s' % (x, y)
        self._field = 'name'
        self._name_to_color = {}
        self._symbols = []
        self._water_color = water_color or default_colors.water_color
        self._line_strings = []

    def set_legend(self, legend):
        self._legend = legend

    def set_district_file(self, district_file):
        self._district_file = district_file

    def set_label_formatter(self, label_formatter):
        self._label_formatter = label_formatter

    def set_field(self, field):
        self._field = field

    def set_name_to_color(self, name_to_color):
        self._name_to_color = name_to_color

    def render_to(self, outfile):
        themap = self.make_map()
        _render_coloured_map(themap, outfile, self._view, self._symbols if self._legend else [])

    def add_symbol(self, symbol):
        self._symbols.append(symbol)

    def add_line_string(self, geojson, color, width):
        self._line_strings.append((geojson, color, width))

    def get_transform(self):
        return self._view.transform

    def make_map(self):
        m = mapnik.Map(self._view.width, self._view.height)
        m.srs = '+proj=merc +ellps=WGS84 +datum=WGS84 +no_defs'
        m.background = mapnik.Color(self._water_color)

        s = mapnik.Style() # style object to hold rules

        for (name, color) in self._name_to_color.items():
            rule = make_rule(color)
            rule.filter = mapnik.Filter("[%s] = '%s'" % (
                self._field, name)
            )
            s.rules.append(rule) # now add the rule to the style

        m.append_style('My Style',s)

        ds = mapnik.GeoJSON(file = self._district_file)
        layer = mapnik.Layer('world')

        layer.datasource = ds
        layer.srs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
        layer.styles.append('My Style')

        m.layers.append(layer)

        for (geojson, color, width) in self._line_strings:
            render_line_string(m, geojson, color, width)

        view = self._view
        zoom_to_box(m, view.west, view.south, view.east, view.north)
        return m

def _render_coloured_map(themap, outfile, view, symbols):
    outfile = make_ending_for(outfile, 'png')
    mapnik.render_to_file(themap, outfile, 'PNG')

    legend_box = None
    if symbols:
        legend_box = _add_legend(outfile, symbols)

    if view.transform:
        view.transform(outfile, legend_box)

    if len(sys.argv) > 1:
        os.system('open ' + outfile)

# ===== CHOROPLETH MAP

def make_color_scale(count):
    import colormaps

    inc = len(colormaps._magma_data) / count
    return [
        'rgb(%s%%, %s%%, %s%%)' % tuple([int(round(x * 100)) for x in colormaps._magma_data[inc * ix]])
        for ix in range(count + 1)
    ]

def nicehex(v):
    return hex(v)[2 : ].zfill(2)

def make_color_scale_rgb(count):
    import colormaps

    inc = len(colormaps._magma_data) / count
    return [
        '#%s%s%s' % tuple([nicehex(int(round(x * 256))) for x in colormaps._magma_data[inc * ix]])
        for ix in range(count + 1)
    ]

def make_rule(color):
    r = mapnik.Rule() # rule object to hold symbolizers
    # to fill a polygon we create a PolygonSymbolizer
    polygon_symbolizer = mapnik.PolygonSymbolizer()
    polygon_symbolizer.fill = mapnik.Color(color)
    r.symbols.append(polygon_symbolizer) # add the symbolizer to the rule object

    # to add outlines to a polygon we create a LineSymbolizer
    line_symbolizer = mapnik.LineSymbolizer()
    line_symbolizer.stroke = mapnik.Color('rgb(5%,5%,5%)')
    line_symbolizer.stroke_width = 0.2
    r.symbols.append(line_symbolizer) # add the symbolizer to the rule object
    return r

GRAY = 'rgb(60%, 60%, 60%)'
class ChoroplethMap(ColoredRegionMap):

    def set_district_to_value(self, district_to_value, levels = 10):
        lowest = min([v for v in district_to_value.values() if v != None])
        biggest = max(district_to_value.values())
        inc = (biggest - lowest) / float(levels)

        name_to_color = {}
        colors = make_color_scale(levels)
        for (district, value) in district_to_value.items():
            ix = int(round((value - lowest) / inc)) if value != None else None

            name_to_color[district] = colors[ix] if ix != None else GRAY

        self.set_name_to_color(name_to_color)

        colors = make_color_scale_rgb(levels) # diff syntax
        for ix in range(levels + 1):
            title = self._label_formatter(lowest + ix * inc, lowest + (ix+1) * inc)
            self.add_symbol(maplib.Symbol(None, colors[ix], title = title, shape = maplib.CIRCLE))

# ===== XML MAP

SRS = '+proj=merc +ellps=WGS84 +datum=WGS84 +no_defs'
class XmlMap(maplib.AbstractMap):

    def __init__(self, view):
        maplib.AbstractMap.__init__(self, default_scale = 8)
        self._view = view

    def render_to(self, filename, width = None, height = None, bottom = None,
                  format = 'png'):
        box = project(SRS, east = self._view.east, west = self._view.west,
                      north = self._view.north, south = self._view.south)

        landfile = SHAPEDIR + 'ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp'

        with open('/tmp/mapnik.xml', 'w') as f:
            f.write('''
<Map
    background-color="#88CCFF"
    srs="%s"
    maximum-extent="%s, %s, %s, %s"
>
  <Style name="land">
    <Rule>
      <PolygonSymbolizer fill="#409050" />

      <LineSymbolizer stroke="rgb(85%%,85%%,90%%)" stroke-width="0.2"/>
    </Rule>
  </Style>

  <Layer srs="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs" name="land">
    <StyleName>land</StyleName>
    <Datasource>
      <Parameter name="file">%s</Parameter>
      <Parameter name="type">shape</Parameter>
    </Datasource>
  </Layer>
</Map>
            ''' % (SRS, box.minx, box.maxx, box.miny, box.maxy, landfile))

        # FIXME: use Python API for this instead
        os.system('mapnik-render --map-width %s --map-height %s /tmp/mapnik.xml %s' % (self._view.width, self._view.height, filename))
