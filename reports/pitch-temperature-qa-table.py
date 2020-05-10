
import sys, codecs
import tablelib, sparqllib
import pitch

tab = tablelib.HtmlWriter(codecs.open('pitch-temperature-qa-table.html', 'w', 'utf-8'))
tab.start_table()

tab.header_row('URI', 'LAT', 'LONG', 'TEMP TEXT', 'TEMP', 'CAT', 'COUNTRY')

seen = set()
for (s, lat, lng, t, c) in sparqllib.query_for_rows(pitch.query):
    temp = pitch.get_temp(t)
    tab.row(s, lat, lng, t, temp, pitch.get_category(t, quiet = True), c)

    if s in seen:
        print 'DUPLICATE', s
    else:
        seen.add(s)

tab.end_table()
