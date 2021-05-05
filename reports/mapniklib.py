'''
Implementation of the Map class which generates PNG maps using Mapnik.
'''

import json, sys, os
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

district_file = None
#district_file = '/Users/larsga/prog/python/etno-distrikt/regions.json'
#district_file = '/Users/larsga/prog/python/etno-distrikt/regions-clipped.json'

# ===== NORMAL MAP

class MapnikMap(maplib.AbstractMap):

    def __init__(self, base_map, color = True, transform = None):
        maplib.AbstractMap.__init__(self, default_scale = 8)
        self._base_map = base_map
        self._color = color
        self._transform = transform

    def get_base_map(self):
        return self._base_map

    def get_color(self):
        return self._color

    def render_to(self, filename, width = None, height = None, bottom = None,
                  format = 'png'):
        filename = make_ending_for(filename, format)
        legend_box = _render(self, filename, format)

        if self._transform:
            self._transform(filename, legend_box)

        if len(sys.argv) > 1:
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

def make_simple_map(shapefile = None, west = -5, south = 55, east = 35, north = 67, width = 2000, height = 1200, elevation = ELEVATION_DEFAULT, color = True, speciesfile = None):
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
        _add_species(m, speciesfile)
    if district_file:
        _add_districts(m, district_file)

    zoom_to_box(m, west, south, east, north)
    return m

def zoom_to_box(m, west, south, east, north):
    # the box is defined in degrees when passed in to us, but now that
    # the projection is Mercator, the bounding box must be specified
    # in metres (no, I don't know why). we solve this by explicitly
    # converting degrees to metres
    source = mapnik.Projection('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    target = mapnik.Projection(m.srs)
    trans = mapnik.ProjTransform(source, target)
    thebox = mapnik.Box2d(west, south, east, north)
    m.zoom_to_box(trans.forward(thebox))

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

def _add_species(m, speciesfile):
    'speciesfile = shapefile with species distribution'

    s = mapnik.Style() # style object to hold rules
    r = mapnik.Rule() # rule object to hold symbolizers
    # to fill a polygon we create a PolygonSymbolizer
    polygon_symbolizer = mapnik.PolygonSymbolizer()
    polygon_symbolizer.fill = mapnik.Color('rgb(0,0,0)')
    polygon_symbolizer.fill_opacity = 0.25
    r.symbols.append(polygon_symbolizer) # add the symbolizer to the rule object

    # to add outlines to a polygon we create a LineSymbolizer
    line_symbolizer = mapnik.LineSymbolizer()
    line_symbolizer.stroke = mapnik.Color('rgb(0%,0%,0%)')
    line_symbolizer.stroke_width = 1
    r.symbols.append(line_symbolizer) # add the symbolizer to the rule object
    s.rules.append(r) # now add the rule to the style

    m.append_style('Chorology',s)

    #ds = mapnik.Shapefile(file = speciesfile)
    ds = mapnik.GeoJSON(file = speciesfile)
    layer = mapnik.Layer('shrub')

    layer.datasource = ds
    layer.srs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    layer.styles.append('Chorology')

    m.layers.append(layer)

def _add_districts(m, district_file):
    s = mapnik.Style()
    r = mapnik.Rule()

    # polygon_symbolizer = mapnik.PolygonSymbolizer()
    # polygon_symbolizer.fill = mapnik.Color('rgb(0,0,0)')
    # polygon_symbolizer.fill_opacity = 0.25
    # r.symbols.append(polygon_symbolizer)

    line_symbolizer = mapnik.LineSymbolizer()
    line_symbolizer.stroke = mapnik.Color('rgb(0%,0%,0%)')
    line_symbolizer.stroke_width = 0.5
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
        mapnik.COLORIZER_DISCRETE, mapnik.Color(0, 0, 0, 0)
    )
    #rs.colorizer.add_stop(0, mapnik.Color(217, 217, 229))

    rs.colorizer.add_stop(250, mapnik.Color(58, 130, 72))
    rs.colorizer.add_stop(500, mapnik.Color(37, 117, 69))
    rs.colorizer.add_stop(1000, mapnik.Color(27, 75, 46))

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
    #     base = '/Users/larsga/Desktop/DTM50_UTM33_20200904',
    #     file = 'norge.tif',
    #     band = 1,
    # )
    # srs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'

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


def _render(themap, filename, format):
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

    mapnik.render_to_file(m, filename, format)

    box = None
    if themap.has_legend() and themap.has_symbols() and format == 'png':
        used_symbols = [s for s in themap.get_symbols() if themap.is_symbol_used(s)]
        box = _add_legend(filename, used_symbols)
    return box

def _add_legend(filename, used_symbols):
    from PIL import Image, ImageDraw, ImageFont

    im = Image.open(filename)

    r = 12
    font = ImageFont.truetype('Arial.ttf', r * 2)

    widest = 0
    for symbol in used_symbols:
        width = font.getsize(symbol.get_title())[0]
        widest = max(widest, width)

    offset = 10
    displace = (r * 2) + 12
    x1 = 10
    y1 = 10
    x2 = 10 + r * 2 + offset * 3 + widest
    y2 = 10 + displace * len(used_symbols) + offset
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

def _parse_color(color):
    return (_unhex(color[1 : 3]), _unhex(color[3 : 5]), _unhex(color[5 : 7]))

def _unhex(h):
    return _unhexdigit(h[0]) * 16 + _unhexdigit(h[1])

def _unhexdigit(digit):
    if digit >= '0' and digit <= '9':
        return int(digit)
    else:
        return ord(digit.lower()) - 87

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
class ChoroplethMap:

    def __init__(self, view):
        self._view = view
        self._legend = False
        self._district_file = '/Users/larsga/prog/python/etno-distrikt/regions-clipped.json'
        self._label_formatter = lambda x,y: '%s-%s' % (x, y)

    def set_legend(self, legend):
        self._legend = legend

    def set_district_file(self, district_file):
        self._district_file = district_file

    def set_label_formatter(self, label_formatter):
        self._label_formatter = label_formatter

    def render_to(self, outfile, district_to_value, levels = 10,
                  field_name = 'name'):
        # _render_choropleth_map(outfile, self._view, district_to_value,
        #                        levels, self._legend, self._district_file,
        #                        self._label_formatter)

        lowest = min([v for v in district_to_value.values() if v != None])
        biggest = max(district_to_value.values())
        inc = (biggest - lowest) / float(levels)

        name_to_color = {}
        colors = make_color_scale(levels)
        for (district, value) in district_to_value.items():
            ix = int(round((value - lowest) / inc)) if value != None else None

            name_to_color[district] = colors[ix] if ix != None else GRAY

        symbols = []
        if self._legend:
            colors = make_color_scale_rgb(levels) # diff syntax
            symbols = [maplib.Symbol(None, colors[ix], title = self._label_formatter(lowest + ix * inc, lowest + (ix+1) * inc), shape = maplib.CIRCLE)
                       for ix in range(levels + 1)]

        _render_coloured_map(outfile, self._view, name_to_color,
                             symbols, self._district_file,
                             field_name)

def _render_choropleth_map(outfile, view, district_to_value, levels, legend,
                           district_file):
    outfile = make_ending_for(outfile, 'png')

    m = mapnik.Map(view.width, view.height)
    m.srs = '+proj=merc +ellps=WGS84 +datum=WGS84 +no_defs'
    m.background = mapnik.Color(default_colors.water_color)

    s = mapnik.Style() # style object to hold rules

    lowest = min([v for v in district_to_value.values() if v != None])
    biggest = max(district_to_value.values())
    inc = (biggest - lowest) / float(levels)

    buckets = {}
    for (district, value) in district_to_value.items():
        ix = int(round((value - lowest) / inc)) if value != None else None
        if ix not in buckets:
            buckets[ix] = []
        buckets[ix].append(district)

    colors = make_color_scale(levels)
    for ix in range(levels + 1):
        if ix not in buckets:
            continue

        rule = make_rule(colors[ix])
        rule.filter = mapnik.Filter(' or '.join([
            "[name] = '%s'" % name.encode('utf-8') for name in buckets[ix]
        ]))
        # print ix, u' or '.join([
        #     u"[name] = '%s'" % name for name in buckets[ix]
        # ])
        s.rules.append(rule) # now add the rule to the style

    # None = no value, treated specially
    if None in buckets:
        rule = make_rule('rgb(60%, 60%, 60%)')
        rule.filter = mapnik.Filter(' or '.join([
            "[name] = '%s'" % name.encode('utf-8') for name in buckets[None]
        ]))
        s.rules.append(rule)

    m.append_style('My Style',s)

    ds = mapnik.GeoJSON(file = district_file)
    layer = mapnik.Layer('world')

    layer.datasource = ds
    layer.srs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    layer.styles.append('My Style')

    m.layers.append(layer)

    zoom_to_box(m, view.west, view.south, view.east, view.north)
    mapnik.render_to_file(m, outfile, 'PNG')

    if legend:
        colors = make_color_scale_rgb(levels)
        symbols = [maplib.Symbol(None, colors[ix], title = format_label(lowest + ix * inc, lowest + (ix+1) * inc), shape = maplib.CIRCLE)
            for ix in range(levels + 1)]
        _add_legend(outfile, symbols)

    if len(sys.argv) > 1:
        os.system('open ' + outfile)

# ===== FREE-FORM COLOUR-FILL MAP

class ColoredRegionMap:

    def __init__(self, view):
        self._view = view
        self._legend = False
        self._district_file = '/Users/larsga/prog/python/etno-distrikt/regions-clipped.json'
        self._label_formatter = lambda x,y: '%s-%s' % (x, y)

    def set_legend(self, legend):
        self._legend = legend

    def set_district_file(self, district_file):
        self._district_file = district_file

    def set_label_formatter(self, label_formatter):
        self._label_formatter = label_formatter

    def render_to(self, outfile, name_to_color, field = 'name'):
        _render_coloured_map(outfile, self._view, name_to_color,
                             None, self._district_file, field)

def _render_coloured_map(outfile, view, name_to_color, symbols,
                         district_file, field_name):
    outfile = make_ending_for(outfile, 'png')

    m = mapnik.Map(view.width, view.height)
    m.srs = '+proj=merc +ellps=WGS84 +datum=WGS84 +no_defs'
    m.background = mapnik.Color(default_colors.water_color)

    s = mapnik.Style() # style object to hold rules

    for (name, color) in name_to_color.items():
        rule = make_rule(color)
        rule.filter = mapnik.Filter("[%s] = '%s'" % (
            field_name, name.encode('utf-8'))
        )
        s.rules.append(rule) # now add the rule to the style

    m.append_style('My Style',s)

    ds = mapnik.GeoJSON(file = district_file)
    layer = mapnik.Layer('world')

    layer.datasource = ds
    layer.srs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    layer.styles.append('My Style')

    m.layers.append(layer)

    zoom_to_box(m, view.west, view.south, view.east, view.north)
    mapnik.render_to_file(m, outfile, 'PNG')

    legend_box = None
    if symbols:
        legend_box = _add_legend(outfile, symbols)

    if view.transform:
        view.transform(outfile, legend_box)

    if len(sys.argv) > 1:
        os.system('open ' + outfile)
