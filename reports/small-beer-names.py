#encoding=utf-8

import re
import maputils

LETT = re.compile(u'lettøl')
TYNN = re.compile(u't(o|y|u)n(n|t)(øl|dricka)')
SPISS = re.compile(u'sp(i|y|ø)s(s)?(ö|ø|e)l')
SVAGDRICKA = re.compile(u'svagdricka')

symbols = [
    (LETT,       '#FFFFFF', u'Lettøl'),
    (TYNN,       '#00FFFF', u'Tynnøl'),
    (SPISS,      '#FF00FF', u'Spissøl'),
    (SVAGDRICKA, '#FFFF00', u'Svagdricka'),
]
maputils.make_term_map('tb:small-beer-name', symbols, 'small-beer-names')
