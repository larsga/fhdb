#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The `sparql` module can be invoked in several different ways. To quickly run a
query use :func:`query`. Results are encapsulated in a
:class:`_ResultsParser` instance::

    >>> result = sparql.query(endpoint, query)
    >>> for row in result:
    >>>    print row


Command-line use
----------------

::

    sparql.py [-i] endpoint
        -i Interactive mode

If interactive mode is enabled, the program reads queries from the console
and then executes them. Use a double line (two 'enters') to separate queries.

Otherwise, the query is read from standard input.
"""

__version__ = '0.9'

import copy

import urllib2
from urllib import urlencode
from base64 import encodestring
from string import replace
import compiler
import re
import decimal

from xml.dom import pulldom

USER_AGENT =  "sparql-client/%s +http://www.eionet.europa.eu/software/sparql-client/" % __version__

CONTENT_TYPE = {
                 'turtle' : "application/turtle" ,
                 'n3' :"application/n3",
                 'rdfxml' : "application/rdf+xml" ,
                 'ntriples' : "application/n-triples" ,
                 'xml' : "application/xml" 
                }


RESULTS_TYPES = {
                 'xml' : "application/sparql-results+xml" ,
                 'json' : "application/sparql-results+json" 
                 }

# The purpose of this construction is to use shared strings when
# they have the same value. This way comparisons can happen on the
# memory address rather than looping through the content.
XSD_STRING = 'http://www.w3.org/2001/XMLSchema#string'
XSD_INTEGER = 'http://www.w3.org/2001/XMLSchema#integer'
XSD_LONG = 'http://www.w3.org/2001/XMLSchema#long'
XSD_DOUBLE = 'http://www.w3.org/2001/XMLSchema#double'
XSD_FLOAT = 'http://www.w3.org/2001/XMLSchema#float'
XSD_DECIMAL = 'http://www.w3.org/2001/XMLSchema#decimal'
XSD_DATETIME = 'http://www.w3.org/2001/XMLSchema#dateTime'
XSD_DATE = 'http://www.w3.org/2001/XMLSchema#date'
XSD_TIME = 'http://www.w3.org/2001/XMLSchema#time'
XSD_BOOLEAN = 'http://www.w3.org/2001/XMLSchema#boolean'

datatype_dict = {
                 '': '',
                 XSD_STRING : XSD_STRING,
                 XSD_INTEGER : XSD_INTEGER,
                 XSD_LONG : XSD_LONG,
                 XSD_DOUBLE : XSD_DOUBLE,
                 XSD_FLOAT : XSD_FLOAT,
                 XSD_DECIMAL : XSD_DECIMAL,
                 XSD_DATETIME : XSD_DATETIME,
                 XSD_DATE : XSD_DATE,
                 XSD_TIME : XSD_TIME,
                 XSD_BOOLEAN : XSD_BOOLEAN
                 }

# allow import from RestrictedPython
__allow_access_to_unprotected_subobjects__ = {'Datatype': 1, 'unpack_row': 1,
    'RDFTerm': 1, 'IRI': 1, 'Literal': 1, 'BlankNode': 1}

def Datatype(value):
    """
    Replace the string with a shared string.
    intern() only works for plain strings - not unicode.
    We make it look like a class, because it conceptually could be.
    """
    if value==None:
        r = None
    elif datatype_dict.has_key(value):
        r = datatype_dict[value]
    else:
        r = datatype_dict[value] = value
    return r

class RDFTerm(object):
    """
    Super class containing methods to override. :class:`IRI`,
    :class:`Literal` and :class:`BlankNode` all inherit from :class:`RDFTerm`.
    """

    __allow_access_to_unprotected_subobjects__ = {'n3': 1}

    def __str__(self):
        return str(self.value)

    def __unicode__(self):
        return self.value

    def n3(self):
        """ Return a Notation3 representation of this term. """
        # To override
        # See N-Triples syntax: http://www.w3.org/TR/rdf-testcases/#ntriples
        raise NotImplementedError("Subclasses of RDFTerm must implement `n3`")

    def __repr__(self):
        return '<%s %s>' % (type(self).__name__, self.n3())

class IRI(RDFTerm):
    """ An RDF resource. """

    def __init__(self, value):
        self.value = value

    def __str__(self):
       return self.value.encode("unicode-escape")

    def __eq__(self, other):
       if type(self) != type(other):
           return False
       if self.value == other.value: return True
       return False

    def n3(self):
        return '<%s>' % self.value

_n3_quote_char = re.compile(r'[^ -~]|["\\]')
_n3_quote_map = {
    '"': '\\"',
    '\n': '\\n',
    '\t': '\\t',
    '\\': '\\\\',
}
def _n3_quote(string):
    def escape(m):
        ch = m.group()
        if ch in _n3_quote_map:
            return _n3_quote_map[ch]
        else:
            return "\\u%04x" % ord(ch)
    return '"' + _n3_quote_char.sub(escape, string) + '"'

class Literal(RDFTerm):
    """
    Literals. These can take a data type or a language code.
    """
    def __init__(self, value, datatype=None, lang=None):
        self.value = unicode(value)
        self.lang = lang
        self.datatype = datatype

    def __eq__(self, other):
       if type(self) != type(other):
           return False

       elif (self.value == other.value and
             self.lang == other.lang and
             self.datatype == other.datatype):
           return True

       else:
           return False

    def n3(self):
        n3_value = _n3_quote(self.value)

        if self.datatype is not None:
            n3_value += '^^<%s>' % self.datatype

        if self.lang is not None:
            n3_value += '@' + self.lang

        return n3_value

class BlankNode(RDFTerm):
    """ Blank node. Similar to `IRI` but lacks a stable identifier. """
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
       if type(self) != type(other):
           return False
       if self.value == other.value:
           return True
       return False

    def n3(self):
        return '_:%s' % self.value

_n3parser_lang = re.compile(r'@(?P<lang>\w+)$')
_n3parser_datatype = re.compile(r'\^\^<(?P<datatype>[^\^"\'>]+)>$')

def parse_n3_term(src):
    """
    Parse a Notation3 value into a RDFTerm object (IRI or Literal).

    This parser understands IRIs and quoted strings; basic non-string types
    (integers, decimals, booleans, etc) are not supported yet.
    """

    src = unicode(src)

    if src.startswith('<'):
        # `src` is an IRI
        if not src.endswith('>'):
            raise ValueError

        value = src[1:-1]
        if '<' in value or '>' in value:
            raise ValueError

        return IRI(value)

    else:
        datatype_match = _n3parser_datatype.search(src)
        if datatype_match is not None:
            datatype = datatype_match.group('datatype')
            src = _n3parser_datatype.sub('', src)
        else:
            datatype = None

        lang_match = _n3parser_lang.search(src)
        if lang_match is not None:
            lang = lang_match.group('lang')
            src = _n3parser_lang.sub('', src)
        else:
            lang = None

        # Python literals syntax is mostly compatible with N3.
        # We don't execute the code, just turn it into an AST.
        try:
            ast = compiler.parse("value = u" + src)
        except:
            raise ValueError

        # Don't allow any extra tokens in the AST
        if len(ast.node.getChildNodes()) != 1:
            raise ValueError
        assign_node = ast.node.getChildNodes()[0]
        if len(assign_node.getChildNodes()) != 2:
            raise ValueError
        value_node = assign_node.getChildNodes()[1]
        if value_node.getChildNodes():
            raise ValueError
        if value_node.__class__ != compiler.ast.Const:
            raise ValueError
        value = value_node.value

        if type(value) is not unicode:
            raise ValueError

        return Literal(value, datatype, lang)

#########################################
#
# _ServiceMixin
#
#########################################
class _ServiceMixin:
    def __init__(self, endpoint):
        self._method = "POST"
        self.endpoint = endpoint
        self._default_graphs = []
        self._named_graphs = []
        self._prefix_map = {}

        self._headers_map = {}
        self._headers_map['Accept'] = RESULTS_TYPES['xml']
        self._headers_map['User-Agent'] = USER_AGENT

    def _setMethod(self, method):
        if method in ("GET", "POST"):
            self._method = method

    def _getMethod(self):
        return self._method

    method = property(_getMethod, _setMethod)

    def addDefaultGraph(self, g):
        self._default_graphs.append(g)

    def defaultGraphs(self):
        return self._default_graphs

    def addNamedGraph(self, g):
        self._named_graphs.append(g)

    def namedGraphs(self):
        return self._named_graphs

    def setPrefix(self, prefix, uri):
        self._prefix_map[prefix] = uri

    def prefixes(self):
        return self._prefix_map

    def headers(self):
        return self._headers_map

#########################################
#
# Service
#
#########################################

class Service(_ServiceMixin):
    """
    This is the main entry to the library.
    The user creates a :class:`Service`, then sends a query to it.
    If we want to have persistent connections, then open them here.
    """
    def __init__(self, endpoint, qs_encoding = "utf-8"):
        _ServiceMixin.__init__(self, endpoint)
        self.qs_encoding = qs_encoding

    def createQuery(self):
        q = _Query(self)
        q._default_graphs = copy.deepcopy(self._default_graphs)
        q._headers_map = copy.deepcopy(self._headers_map)
        q._named_graphs = copy.deepcopy(self._named_graphs)
        q._prefix_map = copy.deepcopy(self._prefix_map)
        return q

    def query(self, query):
        q = self.createQuery()
        return q.query(query)

    def authenticate(self, username, password):
        self._headers_map['Authorization'] = "Basic %s" % replace(
                encodestring("%s:%s" % (username, password)), "\012", "")

def _parseBoolean(val):
    if val.lower() in ('true', '1'):
        return True
    else:
        return False


# XMLSchema types and cast functions
_types = {
    XSD_INTEGER: int,
    XSD_LONG: int,
    XSD_DOUBLE: float,
    XSD_FLOAT: float,
    XSD_DECIMAL: decimal.Decimal,
    XSD_BOOLEAN: _parseBoolean,
}

try:
    import dateutil.parser
    _types[XSD_DATETIME] = dateutil.parser.parse
    _types[XSD_DATE] = lambda v: dateutil.parser.parse(v).date()
    _types[XSD_TIME] = lambda v: dateutil.parser.parse(v).time()
except ImportError:
    pass

def unpack_row(row, convert=None, convert_type={}):
    """
    Convert values in the given row from :class:`RDFTerm` objects to plain
    Python values: :class:`IRI` is converted to a unicode string containing
    the IRI value; :class:`BlankNode` is converted to a unicode string with
    the BNode's identifier, and :class:`Literal` is converted based on its
    XSD datatype.

    The library knows about common XSD types (STRING becomes :class:`unicode`,
    INTEGER and LONG become :class:`int`, DOUBLE and FLOAT become
    :class:`float`, DECIMAL becomes :class:`~decimal.Decimal`, BOOLEAN becomes
    :class:`bool`). If the `python-dateutil` library is found, then DATE,
    TIME and DATETIME are converted to :class:`~datetime.date`,
    :class:`~datetime.time` and :class:`~datetime.datetime` respectively.  For
    other conversions, an extra argument `convert` may be passed. It should be
    a callable accepting two arguments: the serialized value as a
    :class:`unicode` object, and the XSD datatype.
    """
    out = []
    known_types = dict(_types)
    known_types.update(convert_type)
    for item in row:
        if item is None:
            value = None
        elif isinstance(item, Literal):
            if item.datatype in known_types:
                to_python = known_types[item.datatype]
                value = to_python(item.value)
            elif convert is not None:
                value = convert(item.value, item.datatype)
            else:
                value = item.value
        else:
            value = item.value
        out.append(value)
    return out

#########################################
#
# _Query
#
#########################################
class _Query(_ServiceMixin):

    def __init__(self, service):
        _ServiceMixin.__init__(self, service.endpoint)

    def _request(self, query):
        """
        Builds the query string, then opens a connection to the endpoint
        and returns the file descriptor.
        """
        resultsType = 'xml'

        query = self._queryString(query)
        if self.method == "GET":
            request = urllib2.Request(self.endpoint + "?" + query, None, self.headers())
        else:
            request = urllib2.Request(self.endpoint, query, self.headers())

        #TODO Handle exceptions
        # You can expect urllib2.URLError errors. This should be encapsulated
        return urllib2.urlopen(request)

    def query(self, query):

        response = self._request(query)
        return _ResultsParser(response.fp)

    def _queryString(self, query):
        """
        Creates the REST query string from the query and graphs.
        """
        args = []
        query = query.replace("\n", " ").encode('utf-8')

        pref = ' '.join(["PREFIX %s: <%s> " % (p, self._prefix_map[p]) for p in self._prefix_map])

        query = pref + query

        args.append(('query', query))

        for uri in self.defaultGraphs():
            args.append(('default-graph-uri', uri))

        for uri in self.namedGraphs():
            args.append(('named-graph-uri', uri))

        return urlencode(args)


class _ResultsParser:
    """
    Parse the XML result.
    """

    __allow_access_to_unprotected_subobjects__ = {'fetchone': 1,
        'fetchmany': 1, 'fetchall': 1, 'hasresult': 1, 'variables': 1}

    def __init__(self, fp):
        self.__fp = fp
        self._vals = []
        self._hasResult = None
        self.variables = []
        self._fetchhead()

    def _fetchhead(self):
        """
        Fetches the head information. If there are no variables in the
        <head>, then we also fetch the boolean result.
        """
        self.events = pulldom.parse(self.__fp)

        for (event, node) in self.events:
            if event == pulldom.START_ELEMENT:
                if node.tagName == 'variable':
                    self.variables.append(node.attributes['name'].value)
                elif node.tagName == 'boolean':
                    self.events.expandNode(node)
                    self._hasResult = (node.firstChild.data == 'true')
                elif node.tagName == 'result':
                    return # We should not arrive here
            elif event == pulldom.END_ELEMENT:
                if node.tagName == 'head' and self.variables:
                    return
                elif node.tagName == 'sparql':
                    return

    def hasresult(self):
        """
        ASK queries are used to test if a query would have a result.  If the
        query is an ASK query there won't be an actual result, and
        :func:`fetchone` will return nothing. Instead, this method can be
        called to check the result from the ASK query.

        If the query is a SELECT statement, then the return value of
        :func:`hasresult` is `None`, as the XML result format doesn't tell you
        if there are any rows in the result until you have read the first one.
        """
        return self._hasResult

    def __iter__(self):
        """ Synonim for :func:`fetchone`. """
        return self.fetchone()

    def fetchone(self):
        """ Fetches the next set of rows of a query result, returning a list.
            An empty list is returned when no more rows are available.
            If the query was an ASK request, then an empty list is returned as
            there are no rows available.
        """
        idx = -1

        for (event, node) in self.events:
            if event == pulldom.START_ELEMENT:
                if node.tagName == 'result':
                    self._vals = [None] *  len(self.variables)
                elif node.tagName == 'binding':
                    idx = self.variables.index(node.attributes['name'].value)
                elif node.tagName == 'uri':
                    self.events.expandNode(node)
                    data = ''.join(t.data for t in node.childNodes)
                    self._vals[idx] = IRI(data)
                elif node.tagName == 'literal':
                    self.events.expandNode(node)
                    data = ''.join(t.data for t in node.childNodes)
                    lang = node.getAttribute('xml:lang') or None
                    datatype = Datatype(node.getAttribute('datatype')) or None
                    self._vals[idx] = Literal(data, datatype, lang)
                elif node.tagName == 'bnode':
                    self.events.expandNode(node)
                    data = ''.join(t.data for t in node.childNodes)
                    self._vals[idx] = BlankNode(data)

            elif event == pulldom.END_ELEMENT:
                if node.tagName == 'result':
                    #print "rtn:", len(self._vals), self._vals
                    yield tuple(self._vals)

    def fetchall(self):
        """ Loop through the result to build up a list of all rows.
            Patterned after DB-API 2.0.
        """
        result = []
        for row in self.fetchone():
            result.append(row)
        return result

    def fetchmany(self, num):
        result = []
        for row in self.fetchone():
            result.append(row)
            num -= 1
            if num <= 0: return result
        return result

def query(endpoint, query):
    """
    Convenient method to execute a query. Exactly equivalent to::

        sparql.Service(endpoint).query(query)
    """
    s = Service(endpoint)
    return s.query(query)

def _interactive(endpoint):
    while True:
        try:
            lines = []
            while True:
                next = raw_input()
                if not next:
                    break
                else:
                    lines.append(next)

            if lines:
                sys.stdout.write("Querying...")
                result = query(endpoint, " ".join(lines))
                sys.stdout.write("  done\n")

                for row in result.fetchone():
                    print "\t".join(map(unicode,row))

                print
                lines = []

        except Exception, e:
            sys.stderr.write(str(e))



if __name__ == '__main__':
    import sys
    import codecs
    from optparse import OptionParser

    try:
        c = codecs.getwriter(sys.stdout.encoding)
    except:
        c = codecs.getwriter('ascii')
    sys.stdout = c(sys.stdout, 'replace')


    parser = OptionParser(usage="%prog [-i] endpoint",
        version="%prog " + str(__version__))
    parser.add_option("-i", dest="interactive", action="store_true",
                help="Enables interactive mode")

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("Endpoint must be specified")

    endpoint = args[0]

    if options.interactive:
        _interactive(endpoint)

    q = sys.stdin.read()
    result = query(endpoint, q)
    for row in result.fetchone():
        print "\t".join(map(unicode,row))
