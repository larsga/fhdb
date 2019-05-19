'''
Reusable utilities to make life with SPARQL easier.
'''

import types, httplib, urlparse, urllib
import sparql

ENDPOINT = 'http://localhost:8890/sparql'
PREFIXES = ''

def query_for_value(query):
    row = sparql.query(ENDPOINT, PREFIXES + query).fetchone()
    try:
        (a, ) = row
        return a[0].value
    except ValueError, e:
        return None

def query_for_list(query):
    return [row[0].value for row in sparql.query(ENDPOINT, PREFIXES + query)]

def value(val):
    if val:
        return val.value
    else:
        return None

def query_for_rows(query):
    return [[value(val) for val in row]
            for row in sparql.query(ENDPOINT, PREFIXES + query)]

REPLS = [('"', '\\"'), ('\n', '\\n'), ('\r', '\\r'), ('\t', '\\t'),
         ('\\', '\\\\')]
def escape(str):
    for (ch, repl) in REPLS:
        str = str.replace(ch, repl)
    return str

def trans(val):
    if type(val) not in types.StringTypes:
        return '"' + str(val) + '"'
    elif ((val.startswith('http://') or val.startswith('https://')) and
          ' ' not in val):
        return '<' + val.strip() + '>'
    else:
        return '"' + escape(val.strip()) + '"'

def acceptable_type(val):
    return type(val) in (bool, str, unicode, int, long, float)

def write_rdf(url, props, graph):
    upd = 'insert into graph <%s> { %s %s . }'
    props = ['<%s> %s' % (prop, trans(val)) for (prop, val) in props
             if acceptable_type(val)]
    upd = upd % (graph, '<' + url + '>', "; ".join(props))
    do_update(upd)

def do_update(update):
    url = urlparse.urlparse(ENDPOINT)
    port = 80
    if ':' in url.netloc:
        (host, port) = url.netloc.split(':')
        port = int(port)
    else:
        host = url.netloc

    if type(update) == unicode:
        update = update.encode('utf-8')
    body = 'query=' + urllib.quote(update)
    headers = {'Content-type' : 'application/x-www-form-urlencoded; charset=utf-8'}

    conn = httplib.HTTPConnection(host, port)
    conn.request('POST', url.path, body, headers)
    resp = conn.getresponse()

    if resp.status > 299:
        print repr(update)
        print resp.read()
        raise Exception('Error %s: %s' % (resp.status, resp.reason))
