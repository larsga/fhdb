#encoding=utf-8

import re
import maputils

LETT = re.compile(u'lettøl')
TYNN = re.compile(u't(o|y|u)n(n|t)(øl|dricka)')
SPISS = re.compile(u'sp(i|y)s(s)?(ö|ø|e)l')

symbols = [
    (LETT,  '#FFFFFF', u'Lettøl'),
    (TYNN,  '#00FFFF', u'Tynnøl'),
    (SPISS, '#FF00FF', u'Spissøl'),
]
maputils.make_term_map('tb:small-beer-name', symbols, 'small-beer-name.html')
