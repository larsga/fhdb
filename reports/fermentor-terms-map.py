#encoding=utf-8

import re
import maputils

GIL = re.compile(u'(g(i|je)|ji)l(saa|sou|så)?')

symbols = [
    (GIL, '#FFFFFF', u'Gil'),
]
maputils.make_term_map('tb:fermentor-term', symbols, 'fermentor-terms-map')
