
import sys, os, argparse
import maplib, mapniklib

def parse_spec(spec, speciesfile = None):
    parts = spec.split(':')

    spec = MapSpecification()
    spec.area = parts[0]
    spec.elevation = 'el' in parts
    spec.color = 'bw' not in parts
    spec.speciesfile = speciesfile
    return spec

def make_map_from_cli_args(speciesfile = None, map_type = 'default'):
    if len(sys.argv) > 1:
        spec = parse_spec(sys.argv[1], speciesfile)

        if spec.area in map_views:
            view = map_views[spec.area]

            if map_type == 'default':
                return mapniklib.MapnikMap(mapniklib.make_simple_map(
                    east = view.east, west = view.west, south = view.south,
                    north = view.north, width = view.width,
                    height = view.height, elevation = spec.elevation,
                    color = spec.color
                ), color = spec.color, transform = view.transform)
            elif map_type == 'choropleth':
                return mapniklib.ChoroplethMap(view)
            elif map_type == 'colored-region':
                return mapniklib.ColoredRegionMap(view)

    return maplib.GoogleMap(61.8, 9.45, 6)

class MapView:
    def __init__(self, east, west, south, north, width = 2000, height = 1200,
                 transform = None):
        self.east = east
        self.west = west
        self.south = south
        self.north = north
        self.width = width
        self.height = height
        self.transform = transform

def norway_montage(filename, legend_box):
    # hacky workaround for broken PIL
    import os
    os.system('gm convert %s /tmp/tst.gif' % filename)

    tmpfile = '/tmp/tst.png'
    os.system('gm convert /tmp/tst.gif %s' % tmpfile)
    #shutil.copyfile(filename, tmpfile)
    # </hack>

    from PIL import Image, ImageDraw
    im = Image.open(open(tmpfile))

    southern_no = im.crop((0, 1440, 720, 2500))   # 720x1060
    northern_no = im.crop((486, 510, 1186, 1570)) # 700x1060

    composite = Image.new('RGB', (1420, 1060))
    composite.paste(southern_no, (0, 0))
    composite.paste(northern_no, (720, 0))

    if legend_box:
        ((x1, y1), (x2, y2)) = legend_box
        legend = im.crop((x1, y1, x2, y2))
        composite.paste(legend, (10, 10))

    draw = ImageDraw.Draw(composite)
    draw.line((720, 0, 720, 1060), (0, 0, 0))

    composite.save(filename, 'PNG')

map_views = {
    'nordic' : MapView(east = 4, west = 30, south = 54.5, north = 65,
                       width = 1800, height = 1400),
    'norway' : MapView(east = 6, west = 12, south = 57.9, north = 63.9,
                       width = 1200, height = 1250),
    'arctic-norway' : MapView(east = 20, west = 30, south = 65, north = 71.5,
                              width = 1200, height = 800),
    'west-nordic' : MapView(east = -4, west = 25, south = 52.5, north = 63.5,
                            width = 1800, height = 1400),
    'europe-all-big' : MapView(east = -15, west = 50, south = 36, north = 71,
                               width = 2000, height = 1400),
    'norway-sweden' : MapView(east = 6, west = 18, south = 57.9, north = 63.9,
                              width = 1800, height = 1200),
    'mid-norway' : MapView(east = 7.5, west = 10, south = 59, north = 63,
                           width = 1400, height = 1200),
    'norway-montage' : MapView(east = 6, west = 30, south = 57.9, north = 71.5,
                               width = 2200, height = 2500,
                               transform = norway_montage),
    'europe' : MapView(east = 4, west = 50, south = 50, north = 65),
    'europe-all' : MapView(east = -7, west = 57, south = 47.5, north = 62.5,
                           width = 2000, height = 1400),
    'west-europe' : MapView(east = -4, west = 28, south = 52.5, north = 63.5,
                            width = 2000, height = 1600),
    'finland' : MapView(east = 23, west = 27, south = 59, north = 64),
    'baltic' : MapView(east = 24, west = 26, south = 53.5, north = 59.7,
                       width = 1600, height = 1200),
    'denmark' : MapView(east = 15.3, west = 7.8, south = 54.5, north = 57.9,
                        width = 1400, height = 1200),
    'estonia' : MapView(east = 24, west = 25.7, south = 57.5, north = 59.7,
                        width = 1600, height = 1000),
    'georgia' : MapView(east = 41, west = 49, south = 40, north = 45,
                        width = 1600, height = 800),
    'baltic' : MapView(east = 19, west = 31.2, south = 53.7, north = 59.9,
                       width = 1200, height = 1200),
}

class MapSpecification:
    def __init__(self):
        self.elevation = False
        self.color = True

# ===== COMMAND-LINE OPTIONS

def get_language():
    return args.lang

def get_file():
    return args.file

def get_country():
    return args.country

def get_plot_style():
    return args.style

def get_format():
    return args.format

# ===== PARSE THE CMD-LINE

parser = argparse.ArgumentParser()
parser.add_argument('spec', nargs = '?')
parser.add_argument('--lang', default = 'en')
parser.add_argument('--file')
parser.add_argument('--country')
parser.add_argument('--style', default = 'ggplot')
parser.add_argument('--format', default = 'png')

args = parser.parse_args()
