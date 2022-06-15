#!/usr/bin/python
USAGE = """
Command-line usage

  python blat.py <graph uri> <ntriples file to upload> <endpoint name>

<endpoint name> needs to exist in the list of endpoints that's defined
in the config files ./blat.rc or $HOME/.blat.rc. If neither of these
are found, we fall back to the original hard coded Hafslund defaults.

The configuration files should contain one entry per line with name
and url separated by the equal sign. It does not support comments yet.

"""

import sys, httplib, urlparse, urllib2, os, subprocess, socket
from datetime import datetime, timedelta

BATCH_SIZE = 1000
CACHE = True

rapper_filename = "rapper"

# these are the original defaults, preserved for backwards compatibility

def read_triples(filename):
    if not filename.endswith(".ttl"):
        return open(filename)
    else:
        return ttl2n3(filename)

def ttl2n3(filename):
    p=subprocess.Popen([rapper_filename, "-q", "-i", "turtle", filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    ret = p.poll()
    if ret <> 0:
        raise Exception, "Error translating with rapper\n%s"%err
    return output.split("\n")

def get_batches(filename):
    batch = []
    for line in read_triples(filename):
        batch.append(line)
        if len(batch) == BATCH_SIZE:
            yield batch
            batch = []
    if len(batch) > 0:
        yield batch

def clear(endpoint, graph):
    runquery(endpoint, "clear graph <%s>" % graph)

def insert(endpoint, graph, filename):
    count = 0
    for batch in get_batches(filename):
        count += len(batch)
        status, reason = insert_string(endpoint, graph, "\n".join(batch))
        print status, reason, "(%s lines)" % count
        if status != 200:
            print 'Failed to load ' + filename
            sys.exit(1)

    write_date(endpoint, graph)
    count += 1

    return count

def write_date(endpoint, graph):
    ntriples = "<%s> <http://www.sdshare.org/2012/extension/lastmodified> '%s'^^xsd:dateTime" % (graph, datetime.now())
    insert_string(endpoint, graph, ntriples)

def insert_string(endpoint, graph, ntriples):
    query = "insert data into <%s> { %s }" % (graph, ntriples)
    return runquery(endpoint, query)

def runquery(endpoint, query):
    body = "query=" + urllib2.quote(query)

    parsedurl = urlparse.urlparse(endpoint)
    conn = httplib.HTTPConnection(parsedurl.netloc)
    headers = {"Content-type" : "application/x-www-form-urlencoded; charset=utf-8"}
    try:
        conn.request("POST", parsedurl.path, body, headers)
    except socket.error, e:
        errf = open("blat_error.txt", "w")
        errf.write('Cannot connect to %s: %s' % (endpoint, e))
        errf.close()
        print 'Cannot connect to %s: %s' % (endpoint, e)
        raise

    resp = conn.getresponse()
    if resp.status != 200:
        errf = open("blat_error.txt", "w")
        s = resp.read()
        errf.write(s)
        errf.close()

        lines = s.split('\n')
        if len(lines) > 20:
            print '\n'.join(lines[ : 20])
        else:
            print s

    return resp.status, resp.reason

def load_endpoints_file(filename):
    endpoints = {}
    try:
        for line in open(filename):
            (name, url) = line.split("=")
            endpoints[name.strip()] = url.strip()
    except IOError:
        pass # It's ok

    return endpoints

def load_endpoints():
    endpoints = {}
    for f in ["blat.rc", os.path.join(get_home(), "blat.rc")]:
        endpoints.update(load_endpoints_file(f))

    # If we find an rc file use that, otherwise fall back to default
    return endpoints or ENDPOINTS

def get_home():
    return os.environ.get("HOME") or os.environ.get("USERPROFILE")

def get_endpoint_url(endpoint_name):
    endpoints = load_endpoints()
    if endpoint_name is None or not endpoint_name in endpoints:
        print "Which endpoint do you want to to use?"
        for item in endpoints.items():
            print "\t%s = %s" % item
        sys.exit(1)
    return endpoints[endpoint_name]

def blat(graph, ntfile, endpoint_url):
    if check_cache(graph, ntfile):
        clear(endpoint_url, graph)
        insert(endpoint_url, graph, ntfile)
    else:
        print '%s not changed, according to cache' % ntfile

def check_cache(graph, ntfile):
    import json, datetime

    ntfile = os.path.join(os.getcwd(), ntfile)

    scriptdir = os.path.split(__file__)[0]
    cachefile = os.path.join(scriptdir, 'rdf-cache.json')
    try:
        cache = json.load(open(cachefile))
    except IOError, e:
        if e.errno == 2:
            cache = {}
        else:
            raise

    (prevfile, prevdate) = cache.get(graph, ('', ''))
    nowdate = datetime.datetime.fromtimestamp(os.stat(ntfile).st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    if prevfile != ntfile or prevdate != nowdate:
        cache[graph] = [ntfile, nowdate]
        json.dump(cache, open(cachefile, 'w'))
        print '%s has changed, loading' % ntfile
        return True # has changed

    return False # not changed

# --- parse command-line

if __name__ == "__main__":
    if not len(sys.argv) == 4:
        print USAGE
        sys.exit(1)

    blat(sys.argv[1], sys.argv[2], sys.argv[3])
