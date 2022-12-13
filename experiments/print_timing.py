''' timing_decorator_perf.py
uses high speed time.perf_counter() new in python3.3
returned value is in fractional seconds
timing of 2 common sort algorithms
tested with Python33/34  by  vegaseat  17oct2014
'''

import time
from functools import wraps


def print_timing(func):
    '''
    create a timing decorator function
    use
    @print_timing
    just above the function you want to time
    '''
    @wraps(func)  # improves debugging
    def wrapper(*arg):
        start = time.perf_counter()  # needs python3.3 or higher
        result = func(*arg)
        end = time.perf_counter()
        fs = '{} took {:.2f} seconds'
        print(fs.format(func.__name__, (end - start)*1000000))
        return result
    return wrapper
