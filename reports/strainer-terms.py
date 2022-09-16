#encoding=utf-8

import re
import maputils

ROST = re.compile(u'r(o|å|aa|ø|u|y)st(a|e|i)?(k(a|e|je)r(et)?|n|kjer|bytta|så|saa)?')

symbols = [
    (ROST, '#FFFFFF', u'Rost'),
]
maputils.make_term_map('tb:strainer-term', symbols, 'strainer-terms')
