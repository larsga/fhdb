
import sys, string, os, codecs
import utils
import sparqllib

def get_format():
    format = 'html'
    if len(sys.argv) > 1:
        format = sys.argv[1]
    return format

def get_country():
    if len(sys.argv) > 2:
        return sys.argv[2]
    return None

def percent(part, whole):
    return int(round(100.0 * part / whole))

def get_class(part, whole):
    percentage = 100.0 * part / whole
    if percentage >= 75:
        return 'above75'
    elif percentage >= 50:
        return 'above50'
    elif percentage >= 10:
        return 'above10'
    elif percentage >= 5:
        return 'above5'
    elif percentage > 0:
        return 'above0'
    else:
        return 'normal'

def get_last_part(uri):
    pos = uri.rfind('/')
    return uri[pos + 1 : ]

def count_by_key(list):
    index = {}
    for v in list:
        index[v] = index.get(v, 0) + 1
    return index.items()

def flatten(listoflists):
    result = []
    for l in listoflists:
        for i in l:
            result.append(i)
    return result

def intersect(list1, list2):
    return set(list1).intersection(set(list2))

COUNTRY_LABELS = {
    'en' : {
        'col0-label' : 'Country',
        'percent'    : 'Percent',
        'count'      : 'Count',
        'accounts'   : 'Accounts',
        'other'      : 'Other',
    },
    'no' : {
        'col0-label' : 'Land',
        'percent'    : 'Prosent',
        'count'      : 'Antall',
        'accounts'   : 'Beskrivelser',
        'other'      : 'Annet',
    }
}

class CountryTable:

    def __init__(self, min_accounts, sort_columns = None, sort_rows = None, row_label = None, lang = 'en', item_label = None):
        self._min_accounts = min_accounts
        self._country = {} # account uri -> country
        self._values = {} # account uri -> values
        self._sort_columns = sort_columns or self.sort_columns
        self._sort_rows = sort_rows or self.sort_countries
        self._other_values = [] # values hidden in 'Other' column
        self._row_label = row_label or COUNTRY_LABELS[lang]['col0-label']
        self._item_label = item_label or COUNTRY_LABELS[lang]['accounts']
        self._lang = lang

    def get_row_label(self):
        return self._row_label

    def get_item_label(self):
        return self._item_label

    def add_account(self, value, country, uri):
        self._country[uri] = country
        self._values[uri] = self._values.get(uri, []) + [value]

    def get_countries(self):
        'Return countries ordered by number of accounts (decreasing).'
        return self._sort_rows()

    def sort_countries(self):
        values = list(count_by_key(self._country.values()))
        values.sort(key = lambda i: -i[1])
        return [c for (c, count) in values]

    def sort_columns(self, columns):
        values = list(count_by_key(flatten(self._values.values())))
        values.sort(key = lambda i: -i[1])
        return [col for (col, count) in values]

    def get_columns(self):
        '''Return values by decreasing frequency. Honour min_accounts. If more
        than one column is omitted => merged into single Other column.'''
        values = list(set(flatten(self._values.values())))
        columns = self._sort_columns(values)

        filtered = [col for col in columns
                    if self.get_value_count(col) >= self._min_accounts]

        if len(filtered) < len(columns):
            self._other_values = [
                col for col in columns
                if self.get_value_count(col) < self._min_accounts
            ]
            filtered.append(COUNTRY_LABELS[self._lang]['other'])

        return filtered

    def get_count(self, value, country):
        'Return the number of accounts with this value for this country.'
        the_values = self._translate(value) # handle 'Others'
        return len(set([
            u for (u, values) in self._values.items()
            if intersect(the_values, values) and self._country[u] == country
        ]))

    def get_value_count(self, value):
        'Return the total number of accounts with this value.'
        the_values = self._translate(value) # handle 'Others'
        return len([u for (u, values) in self._values.items()
                    if intersect(the_values, values)])

    def get_country_count(self, country):
        'Return the total number of accounts from this country.'
        return len([u for (u, c) in self._country.items()
                    if c == country])

    def get_total(self):
        'Return the total number of accounts.'
        return len(self._values.values())

    def _translate(self, value):
        if value == COUNTRY_LABELS[self._lang]['other']:
            return self._other_values
        else:
            return [value]

shorthands = {'United_Kingdom' : 'UK'}
def default_row_label(url):
    name = get_last_part(url)
    name = shorthands.get(name, name)
    return name

def make_table(filename, query, get_column_label, label, caption,
               min_accounts = 0, format = 'html',
               get_row_label = default_row_label,
               row_type_name = None, lang = 'en',
               country = None, simplify_mapping = {}):
    table = CountryTable(min_accounts, row_label = row_type_name, lang = lang)
    if country:
        country = 'http://dbpedia.org/resource/' + country

    # v=value, c=country, s=uri of account
    for (v, c, s) in sparqllib.query_for_rows(query):
        if country == None or country == c:
            table.add_account(simplify_mapping.get(v, v), c, s)

    filename = utils.add_extension(filename, format)

    if format == 'html':
        writer = HtmlWriter(codecs.open(filename, 'w', 'utf-8'))
    elif format == 'latex':
        writer = LatexWriter(codecs.open(filename, 'w', 'utf-8'), label = label,
                             caption = caption,
                             columns = len(table.get_columns()) + 2)
    elif format in ('png', 'pdf'):
        writer = HtmlWriter(codecs.open('/tmp/table.html', 'w', 'utf-8'))
    else:
        assert False, 'Unknown format %s' % format

    if not country:
        write_table(writer, table, get_column_label, get_row_label, lang = lang)
    else:
        write_single_table(writer, table, get_column_label, get_row_label,
                           lang = lang)

    if format == 'png':
        with open('/tmp/capture.js', 'w') as f:
            f.write('''
              var page = require('webpage').create();
              page.open('%s', function() {
                page.render('%s');
                phantom.exit();
              });
            ''' % ('file://tmp/table.html', filename))
            os.system('phantomjs file://tmp/capture.js')
    elif format == 'pdf':
        os.system('wkhtmltopdf /tmp/table.html ' + filename)

    if len(sys.argv) > 1:
        os.system('open %s' % filename)

# herb-table-like
def write_table(writer, table, get_column_label, get_row_label = default_row_label, lang = 'en'):
    writer.start_table()
    writer.new_row()
    writer.header(table.get_row_label())

    columns = table.get_columns()
    for col in columns:
        writer.header(get_column_label(col))

    writer.header(table.get_item_label())

    for country in table.get_countries():
        name = get_row_label(str(country)).strip()

        writer.new_row()
        writer.header(name)
        total = table.get_country_count(country)

        for col in columns:
            used = table.get_count(col, country)
            p = percent(used, total)
            writer.cell('%s %%' % int(p), klass = get_class(used, total),
                        breaking = False)

        writer.header(total)

    writer.new_row()
    writer.header('Total')
    for col in columns:
        count = table.get_value_count(col)
        writer.header(count)

    total = table.get_total()
    writer.header(total)

    writer.new_row()
    writer.header(COUNTRY_LABELS[lang]['percent'])
    for col in columns:
        count = table.get_value_count(col)
        p = percent(count, total)
        writer.header('%s %%' % int(p), klass = get_class(count, total),
                    breaking = False)

    writer.cell('100%')
    writer.end_table()

def write_single_table(writer, table, get_column_label, get_row_label = default_row_label, lang = 'en'):
    writer.start_table()
    writer.new_row()
    writer.header(table.get_row_label())
    writer.header(COUNTRY_LABELS[lang]['count'])
    writer.header(COUNTRY_LABELS[lang]['percent'])

    # there's only going to be one country
    for country in table.get_countries():
        total = table.get_country_count(country)
        for col in table.get_columns():
            writer.new_row()
            writer.header(get_column_label(col))
            used = table.get_count(col, country)

            writer.cell(used)
            p = percent(used, total)
            writer.cell('%s %%' % int(p), klass = get_class(used, total),
                        breaking = False)

    writer.new_row()
    writer.header('Total')
    writer.header(table.get_total())
    writer.cell('100%')
    writer.end_table()

# property table
def property_table(outf, query, properties):
    objects = {}
    for (s, p, o) in sparqllib.query_for_rows(query):
        if s in objects:
            k = objects[s]
        else:
            k = {} #{'number' : rdfutils.get_number_from_uri(str(s))}
            objects[s] = k

        k[str(p)] = o

    outf.write('<table>\n')
    outf.write('<tr>\n')

    for (url, label, func, help) in properties:
        if not help:
            outf.write('<th>%s\n' % label)
        else:
            outf.write('<th><span title="%s">%s</span>' % (help, label))

    for k in objects.values():
        outf.write('<tr>')
        #out.write('<tr><td><a href="#kv%s">%s</a>' % (k['number'], k['number']))
        for (url, label, func, help) in properties:
            v = k.get(url)
            if v:
                v = func(v)
            v = (v or '&nbsp;').encode('utf-8')

            outf.write('<td>%s' % v)
            outf.write('\n')

    outf.write('</table>\n')

def identity(v):
    return v

def find_label(p):
    query = '''
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    select ?o where {
      <%s> rdfs:label ?o
    }
    '''
    return sparqllib.query_for_value(query % p)

def boolean(b):
    bool = {
        'false' : False,
        'true' : True,
        '0' : False,
        '1' : True
    }[b]

    if bool:
        return 'Y'
    else:
        return 'N'

def write_simple_table(out, rows):
    writer = HtmlWriter(out)
    writer.start_table()
    for row in rows:
        writer.new_row()
        for v in row:
            writer.cell(v)
    writer.end_table()

class TableWriter:

    def start_table(self):
        pass

    def header_row(self, *cells):
        self.new_row()
        for cell in cells:
            self.header(cell)

    def row(self, *cells):
        self.new_row()
        for cell in cells:
            self.cell(cell)

    def new_row(self):
        pass

    def header(self, content, klass = None, breaking = False):
        pass

    def cell(self, content, klass = None, breaking = True):
        pass

    def end_table(self):
        pass

    # def header_row(self, *cells):
    #     self.new_row()
    #     for cell in cells:
    #         self.header(cell)

    # def row(self, *cells):
    #     self.new_row()
    #     for cell in cells:
    #         self.cell(cell)

class HtmlWriter(TableWriter):

    def __init__(self, out, label = None, caption = None):
        self.out = out
        self.out.write('''
        <style>
          th { text-align: left }
          td.above75 { background-color: #FF6666 }
          td.above50 { background-color: #FFAA00 }
          td.above10 { background-color: #FFFF00 }
          td.above5 { background-color: #D0FFD0 }
          td.above0 { background-color: #EEEEEE }
          /* td, th { padding-right: 12pt }*/
        </style>
        ''')

    def start_table(self):
        self.out.write('<table>\n')

    def new_row(self):
        self.out.write('\n<tr>')

    def header(self, content, klass = None, breaking = False):
        self.out.write('<th')
        if klass:
            self.out.write(' class="%s">' % klass)
        else:
            self.out.write('>')
        self.out.write(str(content))

    def cell(self, content, klass = None, breaking = True):
        self.out.write('<td')
        if klass:
            self.out.write(' class="%s">' % klass)
        else:
            self.out.write('>')

        content = str(content)
        if not breaking:
            content = content.replace(' ', '&nbsp;')
        self.out.write(content)

    def end_table(self):
        self.out.write('</table>\n')
        self.out.close()

colormap = {
    'above75' : '\cellcolor{Red}',
    'above50' : '\cellcolor{YellowOrange}',
    'above10' : '\cellcolor{Yellow}',
    'above5' : '\cellcolor{YellowGreen}',
    'above0' : '\cellcolor[gray]{0.9}',
}

class LatexWriter(TableWriter):

    def __init__(self, out, label, caption, columns):
        self.out = out
        self._first_cell = True
        self._first_row = True
        self._label = label
        self._caption = caption
        self._columns = columns

    def start_table(self):
        self.out.write('\\begin{table}\n')
        self.out.write('\\begin{center}\n')
        self.out.write('\\begin{tabular}')
        self.out.write('{|%s|}' % ('|'.join(['l'] * self._columns)))
        self.out.write('\n')

    def new_row(self):
        if not self._first_row:
            self.out.write('\\\\')
        else:
            self.out.write('\\hline')
        self.out.write('\n')

        self._first_row = False
        self._first_cell = True

    def header(self, content, klass = None, breaking = False):
        if not self._first_cell:
            self.out.write(' & ')
        self._first_cell = False
        self.out.write('\\textbf{%s}' % escape(str(content)))

    def cell(self, content, klass = None, breaking = True):
        if not self._first_cell:
            self.out.write(' & ')
        self._first_cell = False

        if klass in colormap:
            self.out.write(colormap[klass])

        self.out.write(escape(str(content)))

    def end_table(self):
        self.out.write('\\\\\n')
        self.out.write('\\hline\n')
        self.out.write('\\end{tabular}\n')
        self.out.write(u'\\caption{%s}\label{%s}\n' % (self._caption, self._label))
        self.out.write('\\end{center}\n')
        self.out.write('\\end{table}\n')

def escape(s):
    return s.replace(u'%', u'\\%').replace(u'_', u' ')

class ConsoleWriter(TableWriter):

    def __init__(self, out, label = None, caption = None, columns = None):
        self.out = out
        self.rows = []

    def start_table(self):
        pass

    def new_row(self):
        self.rows.append([])

    def header(self, content, klass = None, breaking = False):
        self.cell(content)

    def cell(self, content, klass = None, breaking = True):
        self.rows[-1].append(str(content))

    def end_table(self):
        col_widths = [0] * len(self.rows[0])
        for row in self.rows:
            for ix in range(len(row)):
                col_widths[ix] = max(col_widths[ix], len(row[ix]))

        for row in self.rows:
            line = [row[ix].ljust(col_widths[ix]) for ix in range(len(row))]
            print('  '.join(line))

class TabWriter(TableWriter):
    '''Just writes the table as a tab-separated file. Good for copying and
    pasting into spreadsheets and word processor tables.'''

    def __init__(self, out, label = None, caption = None, columns = None):
        self.out = out
        self._first_row = True
        self._first_cell = True

    def new_row(self):
        if self._first_row:
            self._first_row = False
        else:
            self.out.write('\n')

        self._first_cell = True

    def header(self, content, klass = None, breaking = False):
        self.cell(content)

    def cell(self, content, klass = None, breaking = True):
        if not self._first_cell:
            self.out.write('\t')

        self.out.write(unicode(content))
        self._first_cell = False

    def end_table(self):
        self.out.write('\n')
