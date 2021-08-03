# encoding=utf-8

import codecs
import sparqllib
import tablelib

country = 'Norway'
format = 'latex'
LANG = 'no'
total = True
repeating = False
repeating_filter = True

repfilter = ''
if repeating_filter:
    repfilter = '?event tb:repeating-event %s' % str(repeating).lower()

query = '''
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix neg: <http://www.garshol.priv.no/2014/neg/>
prefix dbp: <http://dbpedia.org/resource/>
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT DISTINCT ?s ?event
WHERE {
  ?s dc:title ?title;
    tb:part-of ?c;
    tb:brew-for ?event.

  FILTER( ?c = dbp:%s )
  %s
}''' % (country, repfilter)

headers = {
    'no' : ['Anledning', 'Beskrivelser', 'Prosent'],
    'en' : ['Event', 'Accounts', 'Percentage']
}
labels = {
    'no' : {'total' : 'Antall'},
    'en' : {'total' : 'Total'},
}

accounts = set()
events = {}
for (url, event) in sparqllib.query_for_rows(query):
    accounts.add(url)
    events[event] = events.get(event, 0) + 1

def clean(label):
    if type(label) in (type(''), type(u'')):
        return label
    return label.value

def prefer(l1, l2):
    if not l2:
        return True

    if l1.lang == LANG:
        return True
    if l2.lang == LANG:
        return False

    if (not l1.lang) and l2.lang:
        return True

    return True

query = '''
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>

SELECT DISTINCT ?s ?label
WHERE {
  ?s a tb:Event;
    rdfs:label ?label.
}'''
event_labels = {}
for (event, label) in sparqllib.query_for_rows_raw(query):
    prev = event_labels.get(str(event))
    if prefer(label, prev):
        event_labels[str(event)] = label

outf = codecs.open('brew-for-table-country.tex', 'w', 'utf-8')
tab = tablelib.LatexWriter(outf, 'tbl-brew-for-country', u'''
Antall kilder som oppgir at man brygget til ulike anledninger.
Summerer til mer enn 100% fordi mange brygget til mer enn én anledning.
''', 3)
tab.start_table()
tab.header_row(headers[LANG][0], headers[LANG][1], headers[LANG][2])

events = events.items()
events.sort(key = lambda e: -e[1])
for (event, count) in events:
    p = round(float(count) / len(accounts) * 1000) / 10.0
    #print repr(clean(event_labels.get(event, event)))
    tab.row(clean(event_labels.get(event, event)), count, '%s %%' % p)

if total:
    tab.row(labels[LANG]['total'], len(accounts), '')

tab.end_table()
outf.close()
