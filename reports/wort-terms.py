#encoding=utf-8

import re
import maputils

VORTER = re.compile('v(ø|ö)rt(er?)?')

symbols = [
    (VORTER, '#FFFFFF', u'Vørter'),
]
maputils.make_term_map('tb:wort-term', symbols, 'wort-terms')
