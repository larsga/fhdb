'''
Utilities for classifying brewing processes.
'''

try:
    import sparqllib
except ImportError:
    pass # this is python2

BORDERLINE = 'http://www.garshol.priv.no/2014/neg/borderline'
STEP_MASH_MIN_STEPS = 2

FULL_QUERY = '''
    prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
    SELECT ?proc ?p ?o
    WHERE {
      ?proc a tb:Process;
        ?p ?o.
    }
'''

# ===== UTILITIES

def intornone(v):
    return int(v) if v != None else None

def boolornone(v):
    if v == 'true':
        return True
    elif v == 'false':
        return False
    elif v == None or v == BORDERLINE:
        return v
    else:
        assert False

def identity(v):
    return v

def strornone(v):
    return str(v) if v != None else None

# ===== PROPERTIES

RDFS = 'http://www.w3.org/2000/01/rdf-schema#'
DC = 'http://purl.org/dc/elements/1.1/'
TB = 'http://www.garshol.priv.no/2014/trad-beer/'
PROPERTIES = {
    RDFS + 'label' : (identity, '_name'),
    DC + 'description' : (identity, '_desc'),
    TB + 'stones-in-mash' : (boolornone, '_stones'),
    TB + 'ferment-in-mash' : (boolornone, '_inmash'),
    TB + 'mash-in-oven' : (boolornone, '_inoven'),
    TB + 'mash-boiled' : (boolornone, '_mashboil'),
    TB + 'mash-kettle-heated' : (boolornone, '_mashkettle'),
    TB + 'infusion-mash-steps' : (intornone, '_inf'),
    TB + 'mash-circulation-rounds' : (intornone, '_circ'),
    TB + 'wort-boiled' : (boolornone, '_wboil'),
    TB + 'mash-circulate-strainer' : (boolornone, '_circ_strain'),
    TB + 'primary-mash-heating' : (strornone, '_primary_mash'),
    TB + 'hop-treatment' : (strornone, '_hop_treatment'),
}
TB_BOIL_HOPS_IN_WORT = TB + 'boil-hops-in-wort'
TB_BOIL_HOPS_IN_MASH = TB + 'boil-hops-in-mash'

TB_MASH_MAPPING = {
    TB + 'mixed' : 'Mixed',
    TB + 'oven' : 'Oven',
    TB + 'infusion' : 'Infusion',
    TB + 'kettle' : 'Kettle',
    TB + 'unknown' : None,
    TB + 'external' : 'External',
}

# ===== FUNCTIONS

def load_processes():
    return load_process_dict().values()

def load_process_dict():
    by_uri = {}
    for (s, p, o) in sparqllib.query_for_rows(FULL_QUERY):
        if s not in by_uri:
            by_uri[s] = Process(s)
        by_uri[s].add_property(p, o)
    return by_uri

def classify_processes():
    return {proc._url : proc.get_category() for proc in load_processes()}

def verify_classification_complete(by_class):
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

def classify_main_heating():
    return {proc._url : proc.get_main_heating() for proc in load_processes()}

# ===== PROCESS

class Process:

    def __init__(self, url):
        self._url = url
        self._name = None
        self._desc = None
        self._stones = None
        self._inmash = None
        self._inoven = None
        self._mashboil = None
        self._mashkettle = None
        self._circ = None
        self._inf = None
        self._wboil = None
        self._circ_strain = None
        self._primary_mash = None
        self._hop_treatment = None

    def add_property(self, p, o):
        if p not in PROPERTIES:
            return

        (func, slot) = PROPERTIES[p]
        setattr(self, slot, func(o))

    def get_no(self):
        ix = self._url.rfind('/')
        return self._url[ix + 1 : ]

    def get_name(self):
        return self._name

    def get_desc(self):
        return self._desc

    def is_mashing_fully_defined(self):
        return None not in [self._inf, self._circ, self._mashkettle,
                            self._mashboil, self._stones]

    # <mashing classification>

    def is_single_infusion(self):
        # deliberately triggering error if inf == None
        return self._inf > 0 and self._inf < 2

    def is_multistep_infusion(self):
        # deliberately triggering error if inf == None
        return self._inf >= 2

    def is_decoction(self):
        return self._circ > 0 and not self._circ_strain

    def is_circulation(self):
        return self._circ > 0 and self._circ_strain

    def is_kettle_mash(self):
        assert type(self._mashkettle) == bool
        return self._mashkettle

    def is_mash_boiled(self):
        assert type(self._mashboil) == bool
        return self._mashboil

    def is_stone_mash(self):
        assert type(self._stones) == bool
        return self._stones

    def is_oven_based(self):
        return bool(self._inoven)

    # </mashing classification>

    def infusion_steps_in_range(self, low, high):
        # high is exclusive

        if self._inf == None:
            return False
        return low <= self._inf < high

    def mash_is_circulated(self):
        return self._circ != None and self._circ > 0

    def get_category(self):
        if self._inmash:
            return 'Ferment mash'
        elif self._inoven:
            return 'Oven'
        elif self._stones:
            return 'Stone'
        elif self._mashboil or self._mashkettle or self._circ or (self._inf and self._inf >= STEP_MASH_MIN_STEPS):
            return 'Complex mash'
        elif self.infusion_steps_in_range(1, STEP_MASH_MIN_STEPS):
            if self._wboil == False:
                return 'Raw ale'
            elif self._wboil in (True, BORDERLINE):
                return 'Boiled'
            else:
                assert False

        print('%s: %s' % (self.get_no(), self._name))
        return None

    def get_main_heating(self):
        if self._primary_mash:
            return TB_MASH_MAPPING[self._primary_mash]
        else:
            return self._infer_main_heating()

    def _infer_main_heating(self):
        if self._inf and self._stones == False and self._inoven == False and self._mashkettle == False and self._circ == 0:
            return 'Infusion'
        elif self._mashkettle and self._inf == 0 and self._stones == False and self._inoven == False and self._circ == 0:
            return 'Kettle'
        elif self._circ and self._mashkettle == False and self._inf == 0 and self._stones == False and self._inoven == False:
            return 'External'
        elif self._inoven and self._mashkettle == False and self._inf == 0 and self._stones == False and self._circ == 0:
            return 'Oven'
        elif self._stones == True and self._inoven == False and self._mashkettle == False and self._inf == 0 and self._circ == 0:
            return 'Stone'

    def verify(self):
        # hop-treatment
        if self._hop_treatment == TB_BOIL_HOPS_IN_WORT:
            assert self._wboil, 'Hop treatment: boil in wort requires wort to be boiled (%s)' % self.get_no()
        elif self._hop_treatment == TB_BOIL_HOPS_IN_MASH:
            assert self._mashboil, 'Hop treatment: boil in mash requires mash to be boiled (%s)' % self.get_no()

        # mash-circulation-rounds
        if self.mash_is_circulated():
            assert self._circ_strain != None, 'Circulation straining must be specified (%s)' % self.get_no()

        # primary-mash-heating
        if self._infer_main_heating() == None:
            assert self._primary_mash != None, 'Primary mashing must be specified (%s)' % self.get_no()
