# encoding=utf-8

import config
import sparqllib

LANG = config.get_language()

from matplotlib import pyplot
pyplot.style.use(config.get_plot_style())

# ===== GET DATA

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?s ?title ?lat ?batch
WHERE {
  ?s dc:title ?title;
    tb:annual-malts-consumption ?batch;
    geo:lat ?lat.
}'''

x = []
y = []
for (s, title, lat, batch) in sparqllib.query_for_rows(query):
    #print title, repr(lat), repr(batch)
    x.append(float(lat))
    y.append(float(batch))

# ===== DO SCATTER PLOT

h = pyplot.scatter(x, y)
pyplot.xlabel({
    'en' : 'Latitude',
    'no' : 'Breddegrad',
}[LANG])
pyplot.ylabel({
    'en' : 'Malts (kg)',
    'no' : 'Malt (kg)',
}[LANG])
pyplot.title({
    'en' : 'Annual malt consumption by latitude',
    'no' : u'Årlig maltforbruk etter breddegrad'
}[LANG])

# ===== LINEAR REGRESSION
import numpy as np
from sklearn.linear_model import LinearRegression

xarr = np.array(x).reshape((-1, 1)) # recast to 2d array, as required
yarr = np.array(y)

model = LinearRegression()
model.fit(xarr, yarr)

intercept = model.intercept_ # constant offset
coeff = model.coef_[0]       # linear factor

STEPS = 100
low_x = min(x)
high_x = max(x)
inc = (high_x - low_x) / STEPS

new_x = [low_x + inc * ix for ix in range(STEPS)]
new_y = [intercept + coeff * x for x in new_x]

#pyplot.legend(loc='upper right')
pyplot.plot(new_x, new_y, 'b')

# ===== MAKE DIAGRAM

if config.get_file():
    pyplot.savefig(config.get_file())
else:
    pyplot.show()
