#encoding=utf-8

import re
import maputils

KVEIK = re.compile('kvei(k|g)')
GANG = re.compile(u'g(a|å|o|aa|ø)ng')
GJAR = re.compile(u'(øl)?(gj|j|g)(æ|ä)r')
JAL = re.compile(u'g?j(a|æ|ä)la?')
GJEST = re.compile(u'(g|j|gj)(æ|ä|e|ei)st?(e?r)?')
BERM = re.compile(u'b(e|æ|a)rm')

symbols = [
    (KVEIK, '#FFFFFF', 'Kveik'),
    (GANG, '#00FFFF', 'Gong'),
    (GJAR, '#FFFF00', u'Gjær'),
    (JAL, '#FFBB66', u'Jäl'),
    (GJEST, '#FF00FF', 'Gjest(er)'),
    (BERM, '#FF0000', 'Berm'),
]
maputils.make_term_map('tb:yeast-term', symbols, 'yeast-terms.html')
