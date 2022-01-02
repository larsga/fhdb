# encoding=utf-8

import config
import tablelib

MIN_ACCOUNTS = 1

LANG = config.get_language()
labels = {'en' : {
        'women' : 'Women',
        'men' : 'Men',
        'either' : 'Either'
    },
    'no' : {
        'women' : 'Kvinner',
        'men' : 'Menn',
        'either' : 'Begge'
    }
}

def get_name(url):
    ix = url.rfind('/')
    return url[ix + 1 : ]

query = '''
prefix tb: <http://www.garshol.priv.no/2014/trad-beer/>
prefix dbp: <http://dbpedia.org/resource/>
SELECT ?sex ?c ?s
WHERE {
  ?s
    dc:title ?title;
    tb:brewer-sex ?sex;
    tb:part-of ?c.

  ?c a dbp:Country.
}''' # <http://www.garshol.priv.no/2021/landsdel/Landsdel>
tablelib.make_table('sex-table.html', query, get_name,
                    label = 'brewer-gender',
                    caption = '',
                    min_accounts = MIN_ACCOUNTS,
                    format = 'html')
