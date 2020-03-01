#encoding=utf-8

import re
import maputils

KORNOL = re.compile(u'k((orn)|(ønnj))øl')
HEIMABRYGG = re.compile('heim(a|e)br(y|u)gg')
MALTOL = re.compile(u'maltøl')
DRICKA = re.compile(u'dr(i|e)(c|k)k(a|e)?')

symbols = [
    (KORNOL,     '#FFFFFF', u'Kornøl'),
    (HEIMABRYGG, '#0000FF', u'Heimabrygg'),
    (MALTOL,     '#00FF00', u'Maltøl'),
    (DRICKA,     '#FF0000', u'Dricka'),
]
maputils.make_term_map('tb:beer-name', symbols, 'beer-name-map')
