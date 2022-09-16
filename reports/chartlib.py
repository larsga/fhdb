
from PIL import Image

def combine_charts(images, per_row, filename):
    '''images: file names as strings
    per_row: number of images per row
    filename: output filename'''

    images = [Image.open(image) for image in images]
    widths, heights = zip(*(i.size for i in images))

    width = int(max(widths)) * per_row
    rows = int((len(images) / per_row) + min(1, len(images) % per_row))
    height = int(max(heights)) * rows

    new_im = Image.new('RGB', (width, height))

    y_offset = 0
    x_offset = 0
    for ix in range(len(images)):
      if ix == 0:
          pass
      elif ix % per_row == 0:
          y_offset += max(heights)
          x_offset = 0
      else:
          x_offset += max(widths)

      #print ix, (x_offset, y_offset), images[ix]
      new_im.paste(images[ix], (x_offset, y_offset))

    new_im.save(filename)
