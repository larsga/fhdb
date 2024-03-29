#encoding=utf-8

import re
import maputils

LETT = re.compile(u'lettøl')
LETTDRIKKE = re.compile('lett(a|e)dr(i|y)kk(a|e)?')
TYNNOL = re.compile(u't(o|y|u|ø)n(n|t|d)(øl|dr(i|e)(c|k)k(a|e)?)')
TYNNING = re.compile(u'tynning')
SPISS = re.compile(u'sp(i|y|ø|e)s(s)?(ö|ø|e|i)l(l)?')
SVAGDRICKA = re.compile(u'svagdri(c|k)k(a|e)')
DRICKA = re.compile(u'dr(e|i)(c|k)k(a|e)?')
DAGLIGOL = re.compile(u'dagligøl')
ETTERLAG = re.compile(u'(e|ä)(i|f)?(t)?te(r)?la(g|ck|k)')
TAPPDREKK = re.compile('t(a|o)pp(e)?dr(e|ø|y)k(k)?')

symbols = [
    (LETT,       '#FFFFFF', u'Lettøl'),
    (LETTDRIKKE, '#CCCCCC', u'Lettdrikke'),
    (TYNNOL,     '#00FFFF', u'Tynnøl'),
    (TYNNING,    '#00FF77', u'Tynning'),
    (SPISS,      '#FF00FF', u'Spissøl'),
    (SVAGDRICKA, '#FFFF00', u'Svagdricka'),
    (DRICKA,     '#AAAA00', u'Dricka'),
    (DAGLIGOL,   '#0000FF', u'Dagligøl'),
    (ETTERLAG,   '#FF0000', u'Etterlag'),
    (TAPPDREKK,  '#AAAAFF', u'Tappdrekk'),
]
maputils.make_term_map(
    'tb:small-beer-name', symbols, 'small-beer-names',
    legend_location = ('top', 'right')
)
