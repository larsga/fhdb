
import sys
import maplib, mapniklib

class MapSpecification:
    def __init__(self):
        pass

def parse_spec(spec):
    parts = spec.split(':')

    spec = MapSpecification()
    spec.area = parts[0]
    spec.elevation = 'el' in parts
    spec.color = 'bw' not in parts
    return spec

def make_map_from_cli_args():
    if len(sys.argv) == 2:
        spec = parse_spec(sys.argv[1])
        if spec.area in locations:
            return locations[spec.area](spec)

    return maplib.GoogleMap(61.8, 9.45, 6)

def make_nordic_map():
    return mapniklib.MapnikMap(mapniklib.make_simple_map(
        east = 4, west = 30, south = 54.5, north = 65,
        width = 1800, height = 1400
    ))

def make_west_nordic_map():
    return mapniklib.MapnikMap(mapniklib.make_simple_map(
        east = -4, west = 25, south = 52.5, north = 63.5,
        width = 1800, height = 1400
    ))

def make_europe_map():
    return mapniklib.MapnikMap(mapniklib.make_simple_map(
        east = 4, west = 50, south = 50, north = 65
    ))

def make_europe_all_map():
    return mapniklib.MapnikMap(mapniklib.make_simple_map(
        east = -7, west = 57, south = 47.5, north = 62.5,
        width = 2000, height = 1400
    ))

def make_finland_map():
    return mapniklib.MapnikMap(mapniklib.make_simple_map(
        east = 23, west = 27, south = 59, north = 64
    ))

def make_baltic_map():
    return mapniklib.MapnikMap(mapniklib.make_simple_map(
        east = 24, west = 26, south = 53.5, north = 59.7,
        width = 1600, height = 1200
    ))

def make_norway_map(spec):
    return mapniklib.MapnikMap(mapniklib.make_simple_map(
        east = 6, west = 12, south = 57.9, north = 63.9,
        width = 1200, height = 1250,
        elevation = spec.elevation,
        color = spec.color
    ))

def make_mid_norway_map(spec):
    return mapniklib.MapnikMap(mapniklib.make_simple_map(
        east = 7.5, west = 10, south = 59, north = 63,
        width = 1400, height = 1200,
        elevation = spec.elevation,
        color = spec.color
    ))

def make_norway_sweden_map(spec):
    return mapniklib.MapnikMap(mapniklib.make_simple_map(
        east = 6, west = 18, south = 57.9, north = 63.9,
        width = 1800, height = 1200,
        elevation = spec.elevation,
        color = spec.color
    ))

def make_denmark_map():
    return mapniklib.MapnikMap(mapniklib.make_simple_map(
        east = 15.3, west = 7.8, south = 54.5, north = 57.9,
        width = 1400, height = 1200
    ))

def make_estonian_map(color = True):
    return mapniklib.MapnikMap(mapniklib.make_simple_map(
        east = 24, west = 25.7, south = 57.5, north = 59.7,
        width = 1600, height = 1000,
        color = color
    ))

def make_georgian_map():
    return mapniklib.MapnikMap(mapniklib.make_simple_map(
        east = 41, west = 49, south = 40, north = 45,
        width = 1600, height = 800
    ))

locations = {
    'europe': make_europe_map,
    'europe-all' : make_europe_all_map,
    'nordic' : make_nordic_map,
    'estonia' : make_estonian_map,
    'georgia' : make_georgian_map,
    'norway' : make_norway_map,
    'mid-norway' : make_mid_norway_map,
    'norway-sweden' : make_norway_sweden_map,
    'denmark' : make_denmark_map,
}
