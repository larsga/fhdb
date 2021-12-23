'''
Utility operations for modifying images.
'''

from PIL import Image

def tile_images(imagelist, rows, outfile):
    'imagelist = list of file names, rows = list of list of image indexes'

    images = [Image.open(i) for i in imagelist]
    widths, heights = zip(*(i.size for i in images))

    width = max(widths) * len(rows[0])
    height = max(heights) * len(rows)

    new_im = Image.new('RGB', (width, height))

    y_offset = 0
    for row in rows:
        x_offset = 0
        for ix in row:
            im = images[ix]
            new_im.paste(im, (x_offset, y_offset))
            x_offset += im.size[0]

        y_offset += im.size[1]

    new_im.save(outfile)

    import sys, os
    if len(sys.argv) > 1:
        os.system('open ' + outfile)
