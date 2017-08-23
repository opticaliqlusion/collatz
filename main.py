import os
import sys
import sympy
import random
import math
import mpmath
import pdb
import pprint

def bin_to_frac(b):
    rval = 0

    x = sympy.Symbol('x')
    p = sympy.Poly(x)

    for c in b:
        p *= 2
        if c == '1':
            p -= 1

    p /= x
    p -= 1

    sols = sympy.solve(p)
    assert len(sols) == 1

    return sols[0]

def frac_to_bin(n,d):
    s = ''
    assert d > n
    x = n
    while True:
        x *= 2
        if x > d:
            s += '1'
            x -= d
        else:
            s += '0'

        if x == n:
            return s

def f(x): return x * 2
def f_1(x): return x/2

def g_1(x): return (3*x+1)/2
def g(x):
    if (2*x-1) % 3 == 0:
        return int((2*x-1) / 3)
    else:
        return None


def first_missing(_list, start=1):
    for i in range(start, len(_list)):
        if i not in _list:
            return i
    return None

def reduce(x):
    rval = ''

    n = x
    while n != 1:
        if n % 2 == 0:
            n = f_1(n)
            rval += '1'
        else:
            n = g_1(n)
            rval += '0'

    return rval

def generate(max=None):
    rval = {}
    todo = [(1,'')]

    print('Generating table...')

    try:
        while len(todo) > 0:

            x, parity_string = todo.pop()

            x1, x2 = f(x), g(x)

            if x1 and (max is None or x1 < max): todo.append((x1, parity_string+'1'))
            if x2 and x2 > 1 and (max is None or x2 < max): todo.append((x2, parity_string+'0'))

            rval[x] = parity_string

            todo = sorted(todo, key=lambda x:x[0])
            todo.reverse()

    except KeyboardInterrupt:
        pass

    print('Filling holes...')

    for k in rval.keys():
        rval[k] = rval[k][::-1]
    
    x = 1
    while True:
        x = first_missing(rval.keys(), start=x)
        if x is None:
            break
        rval[x] = reduce(x)

    return rval

def rotate(l, n):
    n = n % len(l)
    return l[n:] + l[:n]
    
def _pprint(myd, maxkey):
    max_val_len = max(len(str(myd[i])) for i in myd.keys())
    max_key_len = max(len(str(i)) for i in myd.keys())
        
    for key in sorted([i for i in myd.keys() if i < maxkey]):
        print(('[{:>' + str(max_key_len) + '}] {}').format(key, myd[key]))

def main():
    parity_strings = generate(max=int(sys.argv[1]))
    _pprint(parity_strings, 40)
    
    # construct the table
    table = [parity_strings[i] for i in sorted(parity_strings.keys())]
    
    # calculate column sequences and fraction
    results = []
    for column in range(10):
        
        # gather the patter
        pattern = ''
        pattern_length = 2**(column+1)
        i = 0
        
        while True:
            if len(table[i]) < column+1:
                pattern = ''
            else:
                pattern += table[i][column]
                
            if len(pattern) == pattern_length:
                break
                
            i += 1

        pattern = rotate(pattern, -1*(i+1))
        frac = bin_to_frac(pattern)
        
        # assert our fraction works
        test_pattern = frac_to_bin(*frac.as_numer_denom())
        for i in range(1000):
            if len(table[i]) < column + 1: continue
            assert table[i][column] == test_pattern[i % len(test_pattern)]
            
        results.append((float(frac), frac, pattern))

    pdb.set_trace()
    return


if __name__ == "__main__":
    main()