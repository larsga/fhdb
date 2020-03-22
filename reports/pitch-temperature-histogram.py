#encoding=utf-8

import sparqllib
import pitch

BINS = 10

def average(numbers):
    return sum(numbers) / len(numbers)

# ===== ALL IN ONE DATA SET

singles = 0
ranges = 0
milks = 0
bodies = 0

unreadable = 0
temperatures = []
for (s, lat, lng, t, c) in sparqllib.query_for_rows(pitch.query):
    temp = pitch.get_temp(t)
    if temp:
        temperatures.append(temp)
    else:
        unreadable += 1

temperatures.sort()
print temperatures
print 'Interpreted temperatures', len(temperatures)
print 'Unreadable', unreadable
print 'Average', average(temperatures)
# print '  Single', singles
# print '  Range', ranges
# print '  Milk', milks
# print '  Body', bodies

from matplotlib import pyplot
(n, bins, patches) = pyplot.hist(temperatures, BINS, alpha=0.5,
                                 label = 'Pitch temperatures')
pyplot.title('Pitch temperatures')
pyplot.xlabel('Degrees C')
pyplot.ylabel('Number of accounts')
pyplot.show()
