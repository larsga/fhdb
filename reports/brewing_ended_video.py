
import os
import sparqllib, maplib, mapniklib, config

def collect_rows():
    q1 = '''
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT DISTINCT ?s ?lat ?lng ?title ?ended ?year
WHERE {
  ?s
    dc:title ?title;
    geo:lat ?lat;
    geo:long ?lng;
    tb:brewing-ended ?ended.

  OPTIONAL {
    ?s tb:year ?year.
  }
}
    '''

    return [
        (s, lat, lng, title, convert(ended), convert(dated)) for
        (s, lat, lng, title, ended, dated) in
        sparqllib.query_for_rows(q1)
    ]

def convert(year_none_false):
    if year_none_false == None:
        return None
    elif year_none_false == 'false':
        return 'false'
    else:
        return int(year_none_false)

def render_year(year, rows, filename, mapfactory):
    print year
    themap = mapfactory()
    alive = themap.add_symbol('alive', '#FFFF00', '#000000', scale = 8,
                              title = 'Ongoing')
    dead = themap.add_symbol('dead', '#000000', '#000000', scale = 8,
                             title = 'Ended')
    # unknown = themap.add_symbol('unknown', '#AAAAAA', '#000000', scale = 8,
    #                             title = 'Unknown')

    for (s, lat, lng, title, ended, dated) in rows:
        symbol = None
        if ended == 'false':
            if dated != None and dated >= year:
                symbol = alive
            else:
                symbol = None #unknown

        elif ended <= year:
            symbol = dead

        else:
            symbol = alive

        if symbol:
            themap.add_marker(lat, lng, None, symbol)

    themap.set_legend(True)

    themap.render_to(filename)

def add_year(filename, year):
    from PIL import Image, ImageDraw, ImageFont

    im = Image.open(filename)

    font = ImageFont.truetype('Arial.ttf', 36)

    draw = ImageDraw.Draw(im)

    draw.text(
        (200, 15),
        text = str(year),
        fill = (0, 0, 0),
        font = font,
    )

    #im.show()
    im.save(filename, 'PNG')

if __name__ == '__main__':
    rows = collect_rows()
    for year in range(1850, 2000):
        filename = 'video/%04d.png' % (year - 1850)
        render_year(year, rows,
                    filename = filename,
                    mapfactory = config.make_nordic_map)
        add_year(filename, year)

    os.system('ffmpeg -r 5 -f image2 -s 1800x1400 -i video/%04d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p -y brewing-ended.mp4')
