
# The Farmhouse Brewing Database

This repo documents the database structure of the Farmhouse Brewing
Database using RDF. The main files define the classes and properties,
and the main code values for the properties.

It also contains Python code for generating maps, tables, and diagrams
from the database.

The actual data is not here.

## Using the mapping library

Underneath the reports that generate maps is a library for producing
maps with various types of markers on them. That library can produce
both Google Maps output (HTML with embedded JavaScript) or PNG/SVG/PDF
using [mapnik](https://github.com/mapnik/python-mapnik).

For the Google Maps output you need a Google Maps API key.

For the mapnik output you need shapefiles with the various map shapes.

Once you have that using the actual API is simple. Let's say you want
a PNG map of the Nordic countries with a few black and white dots on
it. Then you can do like this:

```
import mapniklib

themap = mapniklib.MapnikMap(mapniklib.make_simple_map(
    # specifies the map region to show
    east = 4, west = 30, south = 54.5, north = 65,
    # specify the size of the PNG
    width = 1800, height = 1400
))

# make the markers we want to place on the map
white = themap.add_symbol('white', '#FFFFFF', '#000000', strokeweight = 1)
black = themap.add_symbol('black', '#000000', '#000000', strokeweight = 1)

# now position the markers
themap.add_marker(59.955535, 11.047497, 'Lillestrom', white)
themap.add_marker(60.629384, 6.418775, 'Voss', black)
themap.add_marker(59.324666, 18.070968, 'Stockholm', white)

# render the map
themap.render_to('nordic.png')
```

If you want to make a Google Map instead, change the first two lines
to:

```
import maplib

themap = maplib.GoogleMap(61.8, 9.45, 6)
```

### Getting a map key

You get Google Maps API keys [from
Google](https://developers.google.com/maps/documentation/javascript/get-api-key).

Once you have the key, put it into the `GOOGLE_MAPS_KEY` environment
variable, and the code will get it from there.

### Getting the shapefiles

The shapefiles for mapnik can be downloaded from [Natural
Earth](http://www.naturalearthdata.com/downloads/). You want the
following:

 * `ne_10m_admin_0_countries`
 * `ne_10m_lakes`
 * `ne_10m_glaciated_areas`
 * `ne_10m_rivers_lake_centerlines`

Make a new directory, and unzip these files into it, so that you have
four subdirectories with the names in the list above.

Then set the `SHAPEDIR` environment variable to point to the directory
that contains these four.

## Requirements

To get the Google Maps output you don't need anything more than just
Python. For mapnik output you need mapnik and python-mapnik.
