
#encoding=utf-8

import re
import maputils

DRAV = re.compile('drav(a)?')
MASK = re.compile(u'm(a|ei|e|ä|æ|ö)sk(sæva)?')

symbols = [
    (DRAV, '#00FF00', 'Drav'),
    (MASK, '#0000FF', 'Mask'),
]
maputils.make_term_map('tb:spent-grain-term', symbols, 'spent-grain-term')
