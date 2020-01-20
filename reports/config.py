
import maplib, mapniklib

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

def make_norway_map():
    return mapniklib.MapnikMap(mapniklib.make_simple_map(
        east = 6, west = 12, south = 57.9, north = 63.9,
        width = 1200, height = 1250
    ))

def make_estonian_map():
    return mapniklib.MapnikMap(mapniklib.make_simple_map(
        east = 24, west = 25.7, south = 57.5, north = 59.7,
        width = 1600, height = 1000
    ))
