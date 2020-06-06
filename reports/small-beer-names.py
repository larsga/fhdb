#encoding=utf-8

import re
import maputils

LETT = re.compile(u'lettøl')
TYNN = re.compile(u't(o|y|u)n(n|t)(øl|dricka)')
SPISS = re.compile(u'sp(i|y|ø)s(s)?(ö|ø|e)l')
SVAGDRICKA = re.compile(u'svagdricka')
DRICKA = re.compile(u'dr(e|i)(c|k)k(a|e)')

symbols = [
    (LETT,       '#FFFFFF', u'Lettøl'),
    (TYNN,       '#00FFFF', u'Tynnøl'),
    (SPISS,      '#FF00FF', u'Spissøl'),
    (SVAGDRICKA, '#FFFF00', u'Svagdricka'),
    (DRICKA,     '#AAAA00', u'Dricka'),
]
maputils.make_term_map('tb:small-beer-name', symbols, 'small-beer-names')
