'''
Implementation of the Map class which generates PNG maps using Mapnik.
'''

import json, sys, os
import mapnik
import maplib

# ===== MAP

class MapnikMap(maplib.AbstractMap):

    def __init__(self, base_map):
        maplib.AbstractMap.__init__(self)
        self._base_map = base_map

    def get_base_map(self):
        return self._base_map

    def render_to(self, filename, width = None, height = None, bottom = None):
        _render(self, filename)
        if len(sys.argv) > 1:
            os.system('open ' + filename)

# ===== SETUP

water_color = '#88CCFF'
#water_color = '#BBBBBB'

def make_simple_map(shapefile = '/Users/larsga/Desktop/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp', west = -5, south = 55, east = 35, north = 67, width = 2000, height = 1200):
    m = mapnik.Map(width, height)
    m.srs = '+proj=merc +ellps=WGS84 +datum=WGS84 +no_defs'
    m.background = mapnik.Color(water_color)

    s = mapnik.Style() # style object to hold rules

    r = mapnik.Rule() # rule object to hold symbolizers
    # to fill a polygon we create a PolygonSymbolizer
    polygon_symbolizer = mapnik.PolygonSymbolizer()
    polygon_symbolizer.fill = mapnik.Color('#409050') # #999999
    r.symbols.append(polygon_symbolizer) # add the symbolizer to the rule object

    # to add outlines to a polygon we create a LineSymbolizer
    line_symbolizer = mapnik.LineSymbolizer()
    line_symbolizer.stroke = mapnik.Color('rgb(10%,10%,10%)')
    line_symbolizer.stroke_width = 0.5
    r.symbols.append(line_symbolizer) # add the symbolizer to the rule object
    s.rules.append(r) # now add the rule to the style

    m.append_style('My Style',s)

    ds = mapnik.Shapefile(file = shapefile)
    layer = mapnik.Layer('world')

    layer.datasource = ds
    layer.srs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    layer.styles.append('My Style')

    m.layers.append(layer)

    _add_lakes(m)
    _add_glaciers(m)
    _add_rivers(m)
#    _add_elevation(m)

    # the box is defined in degrees when passed in to us, but now that
    # the projection is Mercator, the bounding box must be specified
    # in metres (no, I don't know why). we solve this by explicitly
    # converting degrees to metres
    source = mapnik.Projection('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    target = mapnik.Projection(m.srs)
    trans = mapnik.ProjTransform(source, target)
    thebox = mapnik.Box2d(west, south, east, north)
    m.zoom_to_box(trans.forward(thebox))
    return m

def _make_transform(source, target):
    source = mapnik.Projection(source)
    target = mapnik.Projection(target)
    trans = mapnik.ProjTransform(source, target)
    return trans

def _add_lakes(m):
    s = mapnik.Style()
    r = mapnik.Rule()
    polygon_symbolizer = mapnik.PolygonSymbolizer()
    polygon_symbolizer.fill = mapnik.Color(water_color)
    r.symbols.append(polygon_symbolizer)
    s.rules.append(r)

    m.append_style('LakeStyle', s)

    ds = mapnik.Shapefile(file = 'ne_10m_lakes/ne_10m_lakes.shp')
    # ds = mapnik.PostGIS(
    #     host = 'localhost',
    #     dbname = 'larsga',
    #     user = 'larsga',
    #     table = '''
    #       (select way from planet_osm_polygon where
    #            (("natural" in ('water', 'lake')) or water = 'lake') AND
    #            ST_Intersects(way, !bbox!)
    #       ) as foo
    #     '''
    # )
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

    ds = mapnik.Shapefile(file = 'ne_10m_glaciated_areas/ne_10m_glaciated_areas.shp')
    layer = mapnik.Layer('glaciers')
    layer.datasource = ds
    layer.srs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    layer.styles.append('GlacierStyle')
    m.layers.append(layer)

# def _add_elevation(m):
#     s = mapnik.Style()
#     r = mapnik.Rule()
#     sym = mapnik.RasterSymbolizer()
#     sym.opacity = 1
#     sym.scaling = 'bilinear'
#     sym.mode = 'normal'
#     r.symbols.append(sym)
#     s.rules.append(r)

#     m.append_style('HillShade', s)

#     ds = mapnik.Gdal(
#         base = '/Users/larsga/Desktop/DEM_geotiff',
#         file = 'alwdgg.tif',
#     )
#     layer = mapnik.Layer('Elevation')
#     layer.datasource = ds
#     layer.srs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
#     layer.styles.append('HillShade')
#     m.layers.append(layer)

def _add_rivers(m):
    s = mapnik.Style()
    r = mapnik.Rule()
    r.filter = mapnik.Filter("[name] = 'Volga' or [name] = 'Dnipro' or [name] = 'Don' or [name] = 'Kama'")
    line_symbolizer = mapnik.LineSymbolizer()
    line_symbolizer.stroke = mapnik.Color(water_color)
    line_symbolizer.stroke_width = 0.4
    r.symbols.append(line_symbolizer)
    s.rules.append(r)
    m.append_style('RiverStyle', s)

    ds = mapnik.Shapefile(file = '/Users/larsga/Desktop/ne_10m_rivers_lake_centerlines/ne_10m_rivers_lake_centerlines.shp')
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

        f.write('''
            <svg viewBox="0 0 %s %s" xmlns="http://www.w3.org/2000/svg">
              <circle cx="%s" cy="%s" r="%s" stroke="%s" fill="%s"/>
            </svg>
        ''' % (
            size,
            size,
            mid,
            mid,
            mid,
            symbol.get_stroke_color(),
            symbol.get_color()
        ))

def _render(themap, filename):
    m = themap.get_base_map()
    ctx = mapnik.Context()

    symbol_layers = {}
    for symbol in themap.get_symbols():
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

    mapnik.render_to_file(m, filename, 'png')

    if themap.has_legend():
        _add_legend(filename, themap)

def _add_legend(filename, themap):
    from PIL import Image, ImageDraw, ImageFont

    im = Image.open(filename)

    r = 12
    font = ImageFont.truetype('Arial.ttf', r * 2)

    widest = 0
    for symbol in themap.get_symbols():
        width = font.getsize(symbol.get_title())[0]
        widest = max(widest, width)

    offset = 10
    displace = (r * 2) + 12
    x1 = 10
    y1 = 10
    x2 = 10 + r * 2 + offset * 3 + widest
    y2 = 10 + displace * len(themap.get_symbols()) + offset
    draw = ImageDraw.Draw(im)
    draw.rectangle(
        [(x1, y1), (x2, y2)],
        outline = (0, 0, 0),
        fill = (255, 255, 255),
        width = 2,
    )

    for ix in range(len(themap.get_symbols())):
        displacement = displace * ix

        symbol = themap.get_symbols()[ix]
        draw.ellipse(
            [(x1 + offset, y1 + offset + displacement), (x1 + offset + (r * 2), y1 + offset + (r * 2) + displacement)],
            outline = (0, 0, 0),
            fill = _parse_color(symbol.get_color())
        )

        draw.text(
            (x1 + 20 + (r * 2), y1 + 10 + displacement),
            text = symbol.get_title(),
            fill = (0, 0, 0),
            font = font,
        )

    #im.show()
    im.save(filename, 'PNG')

def _parse_color(color):
    return (_unhex(color[1 : 3]), _unhex(color[3 : 5]), _unhex(color[5 : 7]))

def _unhex(h):
    return _unhexdigit(h[0]) * 16 + _unhexdigit(h[1])

def _unhexdigit(digit):
    if digit >= '0' and digit <= '9':
        return int(digit)
    else:
        return ord(digit.lower()) - 87
