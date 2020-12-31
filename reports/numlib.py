'''
Numerical helper functions.
'''

import math

def pretty(num):
    return round(num * 10.0) / 10.0

def avg(values):
    return sum(values) / float(len(values))

def variance(data):
  n = len(data)
  mean = sum(data) / float(n)
  deviations = [(x - mean) ** 2 for x in data]
  return sum(deviations) / float(n)

def stddev(data):
  return math.sqrt(variance(data))

def percent(part, whole):
    return int(round((part / whole) * 100))

def median(values):
    values.sort()
    half = len(values) / 2
    if len(values) % 2 == 0:
        return pretty(avg([values[half], values[half-1]]))
    else:
        return values[half]
