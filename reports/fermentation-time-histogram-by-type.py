#encoding=utf-8

import sparqllib, tablelib, sys
from numlib import *

BINS = 10

NEG = 'http://www.garshol.priv.no/2014/neg/'
GROUPS = {
    "Farmhouse yeast" : [NEG + 'own-yeast'],
    "Brewers' yeast" :  [NEG + 'brewers-yeast'],
    "Lager yeast'"   :  [NEG + 'lager-yeast'],
    "Bakers' yeast"  :  [NEG + 'bakers-yeast', NEG + 'distillers-yeast'],
}

def average(numbers):
    return sum(numbers) / len(numbers)

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix neu: <http://www.garshol.priv.no/2015/neu/>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
prefix uff: <http://www.garshol.priv.no/2015/uff/>

SELECT DISTINCT ?s ?h ?yeast
WHERE {
  ?s dc:title ?title;
    tb:fermentation-time ?h;
    tb:yeast-type ?yeast.
}
'''

groups = {}
for (s, t, group) in sparqllib.query_for_rows(query):
    time = float(t)
    if group not in groups:
        groups[group] = []
    groups[group].append(time)

import numpy
from matplotlib import pyplot

ix = 0
for groupname in GROUPS.keys():
    times = []
    for grpid in GROUPS[groupname]:
        times += groups.get(grpid, [])

    #pyplot.style.use('grayscale')
    (n, bins, patches) = pyplot.hist(
        times, BINS, alpha=0.5,
        label = 'Fermentation times for ' + groupname,
        range = (0, 250)
    )
    pyplot.title('Fermentation times for ' + groupname)
    pyplot.xlabel('Hours')
    pyplot.ylabel('Number of accounts')

    pyplot.savefig('ftime-%s.png' % ix)
    ix += 1
    pyplot.close()

# --- Redo groups

newg = {}
for (title, types) in GROUPS.items():
    for t in types:
        newg[title] = newg.get(title, []) + groups.get(t, [])
groups = {k : v for (k, v) in newg.items() if v}

# --- Stats table

def display_row(title, func):
    out.row(*[title] + [func(groups[g]) for g in groups.keys()])

#out = tablelib.ConsoleWriter(sys.stdout)
out = tablelib.LatexWriter(sys.stdout, 'tbl-by-group',
                           'Statistical summary of values by yeast type.',
                           len(groups) + 1)
out.start_table()

out.header_row(*['Property'] + [g for g in groups.keys()])
display_row('Accounts', len)
display_row('Average', lambda v: pretty(avg(v)))
display_row('Median', median)
display_row('Stddev', lambda v: pretty(stddev(v)))
display_row('<25', lambda v: percent(len([h for h in v if h < 25]), float(len(v))))
display_row('<50', lambda v: percent(len([h for h in v if h < 50]), float(len(v))))
display_row('<75', lambda v: percent(len([h for h in v if h < 75]), float(len(v))))
display_row('>=75', lambda v: percent(len([h for h in v if h >= 75]), float(len(v))))

out.end_table()

# --- Combine

import chartlib
chartlib.combine_charts(['ftime-%s.png' % i for i in range(ix)],
                        2, 'fermentation-time-histogram-by-type.png')

import sys, os
if len(sys.argv) > 1:
    os.system('open fermentation-time-histogram-by-type.png')
