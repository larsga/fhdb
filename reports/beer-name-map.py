#encoding=utf-8

import re
import config
import maputils

KORNOL = re.compile(u'k((o[rd]n)|(ønnj))øl')
HEIMABRYGG = re.compile('heim(a|e)br(y|u)gg')
MALTOL = re.compile(u'malt(ø|ö)l')
DRICKA = re.compile(u'dr(i|e)(c|k)?k(a|e)?')

symbols = [
    (KORNOL,     '#FFFF00', u'Kornøl'),
    (HEIMABRYGG, '#0000FF', u'Heimabrygg'),
    (MALTOL,     '#00FF00', u'Maltøl'),
    (DRICKA,     '#FF0000', u'Dricka'),
]
maputils.make_term_map('tb:beer-name', symbols,
                       config.get_file() or 'beer-name-map',
                       language = config.get_language())
