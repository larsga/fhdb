
import tablelib, sparqllib
import pitch

def sort_columns(cols):
    cols.sort()
    return cols

def column_label(pair):
    return '%s-%s' % pair

def to_pair(v):
    min = v - (v % 5)
    return (int(min), int(min + 5))

columns = [
    (5, 10),
    (10, 15),
    (15, 20),
    (20, 25),
    (25, 30),
    (30, 35),
    (35, 40),
    (40, 45)
]

table = tablelib.CountryTable(1, sort_columns = sort_columns)
for (s, lat, lng, t, c) in sparqllib.query_for_rows(pitch.query):
    temp = pitch.get_temp(t)
    if temp:
        bracket = to_pair(temp)
        table.add_account(bracket, c, s)

out = tablelib.HtmlWriter(open('pitch-temperature-table.html', 'w'))
tablelib.write_table(out, table, column_label)
