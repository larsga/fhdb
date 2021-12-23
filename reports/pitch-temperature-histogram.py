#encoding=utf-8

import config
import sparqllib
import pitch

BINS = 10

def average(numbers):
    return sum(numbers) / len(numbers)

# ===== ALL IN ONE DATA SET

singles = []
ranges = []
milks = 0
bodies = 0
other = 0

unreadable = 0
temperatures = []
q = pitch.make_query(country = config.get_country())
for (s, lat, lng, t, c) in sparqllib.query_for_rows(q):
    temp = pitch.get_temp(t)

    if temp:
        cat = pitch.get_category(t)
        temperatures.append(temp)

        if cat == 'single':
            singles.append(temp)
        elif cat == 'range':
            ranges.append(temp)
        elif cat == 'milkwarm':
            milks +=1
        elif cat == 'body':
            bodies +=1
        else:
            other += 1
    else:
        # print 'UNINTERPRETABLE', t
        unreadable += 1

import numpy

temperatures.sort()
print(temperatures)
print('Interpreted temperatures', len(temperatures))
print('Unreadable', unreadable)
print('Average', average(temperatures))
print('  Single', len(singles), average(singles), numpy.std(singles))
print('  Range', len(ranges), average(ranges), numpy.std(ranges))
print('  Milk', milks)
print('  Body', bodies)
print('  Other', other)

LANG = config.get_language()
label = {
    'en' : 'Pitch temperatures',
    'no' : 'Tilsetningstemperaturer'
}

from matplotlib import pyplot
pyplot.style.use(config.get_plot_style())

(n, bins, patches) = pyplot.hist(temperatures, BINS,
                                 label = label[LANG])
if LANG == 'en':
    pyplot.title('Pitch temperatures')
    pyplot.xlabel('Degrees C')
    pyplot.ylabel('Number of accounts')
elif LANG == 'no':
    pyplot.title('Tilsetningstemperaturer')
    pyplot.xlabel('Grader C')
    pyplot.ylabel('Antall beskrivelser')
else:
    assert False

if not config.get_file():
    pyplot.show()
else:
    pyplot.savefig(config.get_file())
    pyplot.close()
