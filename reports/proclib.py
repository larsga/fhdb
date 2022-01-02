'''
Utilities for classifying brewing processes.
'''

import sparqllib

BORDERLINE = 'http://www.garshol.priv.no/2014/neg/borderline'
STEP_MASH_MIN_STEPS = 2

def classify_processes():
    query = '''
        prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
        SELECT ?proc ?procname ?stones ?inmash ?inoven ?mashboil ?mashkettle ?circ ?inf ?wboil
        WHERE {
          ?proc a tb:Process;
            rdfs:label ?procname.

          OPTIONAL { ?proc tb:stones-in-mash ?stones }
          OPTIONAL { ?proc tb:ferment-in-mash ?inmash }
          OPTIONAL { ?proc tb:mash-in-oven ?inoven }
          OPTIONAL { ?proc tb:mash-boiled ?mashboil }
          OPTIONAL { ?proc tb:mash-kettle-heated ?mashkettle }
          OPTIONAL { ?proc tb:mash-circulation-rounds ?circ }
          OPTIONAL { ?proc tb:infusion-mash-steps ?inf }
          OPTIONAL { ?proc tb:wort-boiled ?wboil }
        }
    '''
    by_cat = {}
    for (proc, procname, stones, inmash, inoven, mashboil, mashkettle, circ, inf, wboil) in sparqllib.query_for_rows(query):
        circ = intornone(circ)
        inf = intornone(inf)

        cat = None
        if inmash == 'true':
            cat = 'Ferment mash'
        elif inoven == 'true':
            cat = 'Oven'
        elif stones == 'true':
            cat = 'Stone'
        elif mashboil == 'true' or mashkettle == 'true' or circ or (inf and inf >= STEP_MASH_MIN_STEPS):
            cat = 'Complex mash'
        elif inf != None:
            if (inf > 0 and inf < STEP_MASH_MIN_STEPS) and wboil == 'false':
                cat = 'Raw ale'
            elif (inf > 0 and inf < STEP_MASH_MIN_STEPS) and wboil in ('true', BORDERLINE):
                cat = 'Boiled'

        # if cat:
        #     print('%s -> %s' % (proc, cat))
        if not cat:
            print('%s: %s' % (proc, procname))

        by_cat[proc] = cat

    return by_cat

def verify_classiciation_complete(by_class):
    query = '''
        prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
        SELECT ?proc
        WHERE {
          ?proc a tb:Process.
        }
    '''
    missing = False
    for proc in sparqllib.query_for_list(query):
        if proc not in by_class:
            print('MISSING PROCESS:', proc)
            missing = True
    return not missing

# ===== UTILITIES

def intornone(v):
    return int(v) if v != None else None
