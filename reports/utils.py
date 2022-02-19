'''
Generally useful functions.
'''

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
        'png' : '.png',
        'html' : '.html',
        'pdf'  : '.pdf',
    }[format]
    if not filename.endswith(extension):
        filename += extension
    return filename

def smallest(numbers):
    return reduce(min, numbers)

def largest(numbers):
    return reduce(max, numbers)
