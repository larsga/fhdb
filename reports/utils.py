'''
Generally useful functions.
'''

import sparqllib

def average(values):
    return sum(values) / float(len(values))

def index(values, keyf = lambda p: p[0], valuef = lambda v: v[1]):
    ix = {}
    for value in values:
        key = keyf(value)
        if key not in ix:
            ix[key] = []

        ix[key].append(valuef(value))
    return ix

def add_extension(filename, format):
    extension = {
        'png'   : '.png',
        'html'  : '.html',
        'pdf'   : '.pdf',
        'latex' : '.tex',
    }[format]
    if not filename.endswith(extension):
        filename += extension
    return filename

def smallest(numbers):
    return reduce(min, numbers)

def largest(numbers):
    return reduce(max, numbers)

# utility for sorting RDF literals
def _better_than(repl, orig, lang):
    if not orig:
        return True

    if repl.lang == lang:
        return True

    return False

def collect_labels(query, lang):
    labels = {}
    for (h, l) in sparqllib.sparql.query(sparqllib.ENDPOINT, query):
        h = sparqllib.value(h)

        n = labels.get(h)
        if _better_than(l, n, lang):
            labels[h] = l

    return {url : sparqllib.value(label) for (url, label)
            in labels.items()}
